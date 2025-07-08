from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.ia_chat import IAChatCreate, IAChatUpdate, IAChatResponse
from app.services.ia_chat import IAChatService
from app.database import get_db, engine
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.chat_service import ChatService
from ai_agent.agent_service import TripPlannerAgent
from ai_agent.models import TripContext, UserPreferences, ChatMessage, AgentResponse
from app.models.trip import Trip
from pydantic import BaseModel
from datetime import datetime, date
import groq
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.sql import select
from app.models.ia_chat import IAChat
from app.models.group import Group
from app.models.user import User
from app.models.group_chat import GroupChat
from dotenv import load_dotenv, dotenv_values
import os

router = APIRouter(prefix="/ia_chat", tags=["IA Chat"])

# Cargar configuración
def get_settings():
    # Debug: Mostrar información sobre el archivo .env
    current_dir = os.getcwd()
    env_path = os.path.join(current_dir, ".env")
    print(f"\n=== Debug: Información del archivo .env ===")
    print(f"Directorio actual: {current_dir}")
    print(f"Ruta del .env: {env_path}")
    print(f"¿Existe el archivo?: {os.path.exists(env_path)}")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            first_line = f.readline().strip()
            print(f"Primera línea del archivo: {first_line}")
    print("==========================================\n")
    
    env_values = dotenv_values(".env")
    return {
        "GROQ_API_KEY": env_values.get("GROQ_API_KEY", ""),
        "MODEL_NAME": "llama-3.1-8b-instant",
        "TEMPERATURE": 0.7,
        "MAX_TOKENS": 4096,
        "TOOLS_ENABLED": True,
        "JSON_MODE": True,
        "AMADEUS_API_KEY": env_values.get("AMADEUS_API_KEY", ""),
        "AMADEUS_API_SECRET": env_values.get("AMADEUS_API_SECRET", ""),
        "WEATHER_API_KEY": None,
        "WEB_SEARCH_ENABLED": True
    }

async def validate_user_and_group(db: AsyncSession, user_id: uuid.UUID, group_id: uuid.UUID) -> bool:
    """Valida que el usuario y grupo existan en group_chat"""
    stmt = select(GroupChat).where(
        GroupChat.user_id == user_id,
        GroupChat.group_id == group_id,
        GroupChat.status == True
    )
    result = await db.execute(stmt)
    return result.first() is not None

@router.get("/test-config")
async def test_config():
    """
    Endpoint de prueba para verificar la configuración
    """
    try:
        config = get_settings()
        return {"message": "Configuración cargada correctamente", "config": config}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return {"message": "Error cargando configuración", "error": str(e), "detail": error_detail}

@router.post("/", response_model=IAChatResponse, status_code=status.HTTP_201_CREATED)
def create_message(chat: IAChatCreate, db: Session = Depends(get_db)):
    try:
        return IAChatService.create_message(db, chat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[IAChatResponse])
def get_all_messages(db: Session = Depends(get_db)):
    return IAChatService.get_all_messages(db)

@router.get("/{message_id}", response_model=IAChatResponse)
def get_message_by_id(message_id: uuid.UUID, db: Session = Depends(get_db)):
    message = IAChatService.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return message

@router.put("/{message_id}", response_model=IAChatResponse)
def update_message(message_id: uuid.UUID, chat_update: IAChatUpdate, db: Session = Depends(get_db)):
    updated = IAChatService.update_message(db, message_id, chat_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return updated

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = IAChatService.delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return

@router.patch("/{message_id}/toggle", response_model=IAChatResponse)
def toggle_status(message_id: uuid.UUID, db: Session = Depends(get_db)):
    toggled = IAChatService.toggle_status(db, message_id)
    if not toggled:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return toggled

@router.get("/user/{user_id}", response_model=List[IAChatResponse])
def get_messages_by_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return IAChatService.get_messages_by_user(db, user_id)

@router.get("/group/{group_id}", response_model=List[IAChatResponse])
def get_messages_by_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    return IAChatService.get_messages_by_group(db, group_id)

@router.get("/user/{user_id}/group/{group_id}", response_model=List[IAChatResponse])
def get_messages_by_user_and_group(user_id: uuid.UUID, group_id: uuid.UUID, db: Session = Depends(get_db)):
    return IAChatService.get_messages_by_user_and_group(db, user_id, group_id)

class ChatRequest(BaseModel):
    message: str
    user_id: uuid.UUID
    group_id: uuid.UUID

class ChatResponse(BaseModel):
    id: uuid.UUID
    message: str
    created_at: datetime
    user_id: uuid.UUID
    group_id: uuid.UUID
    trip_id: Optional[uuid.UUID] = None

# Crear un sessionmaker para sesiones síncronas
SyncSessionLocal = sessionmaker(
    bind=engine.sync_engine,
    class_=Session,
    expire_on_commit=False
)

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_or_create_trip(db: AsyncSession, group_id: uuid.UUID) -> Trip:
    """Obtiene el viaje activo del grupo o crea uno nuevo"""
    stmt = select(Trip).where(
        Trip.group_id == group_id,
        Trip.status == True
    ).order_by(Trip.created_at.desc())
    result = await db.execute(stmt)
    trip = result.scalar_one_or_none()
    
    if not trip:
        # Crear un nuevo viaje
        trip = Trip(
            id=uuid.uuid4(),
            group_id=group_id,
            destination="",  # Se actualizará cuando el agente determine el destino
            start_date=None,  # Se actualizará cuando el agente determine las fechas
            end_date=None,
            status=True
        )
        db.add(trip)
        await db.flush()
    
    return trip

@router.post("/send-message", response_model=ChatResponse)
async def send_message_to_agent(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Envía un mensaje al agente y obtiene su respuesta.
    """
    try:
        # Validar que el usuario y grupo existan
        is_valid = await validate_user_and_group(db, chat_request.user_id, chat_request.group_id)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="El usuario no pertenece al grupo o el grupo no existe"
            )

        # Cargar configuración
        settings = get_settings()
        
        # Obtener o crear el viaje para este grupo
        trip = await get_or_create_trip(db, chat_request.group_id)

        # Guardar el mensaje del usuario
        user_message = IAChat(
            user_id=chat_request.user_id,
            group_id=chat_request.group_id,
            message=chat_request.message
        )
        db.add(user_message)
        await db.flush()

        # Obtener historial de chat
        stmt = select(IAChat).where(
            IAChat.group_id == chat_request.group_id,
            IAChat.status == True
        ).order_by(IAChat.created_at.desc()).limit(10)
        result = await db.execute(stmt)
        chat_history = result.scalars().all()

        # Convertir mensajes a formato ChatMessage
        chat_messages = [
            ChatMessage(
                user_id=msg.user_id,
                message=msg.message,
                created_at=msg.created_at
            ) for msg in chat_history
        ]

        # Crear contexto del viaje
        trip_context = TripContext(
            group_id=chat_request.group_id,
            participants=[
                UserPreferences(
                    user_id=chat_request.user_id,
                    name="Usuario",  # Podríamos obtener el nombre real de la base de datos
                    destinations=[],
                    activities=[],
                    prices=[],
                    accommodations=[],
                    transport=[],
                    motivations=[]
                )
            ],
            chat_history=chat_messages,
            specific_requirements=chat_request.message
        )

        # Inicializar el agente de viajes con una sesión síncrona
        sync_session = SyncSessionLocal()
        try:
            agent = TripPlannerAgent(sync_session)
            
            # Obtener la respuesta del agente
            response: AgentResponse = await run_in_threadpool(
                lambda: agent.generate_itinerary(trip_context, trip.id)
            )
            
            if response.error:
                raise Exception(response.error)
                
            agent_response = response.itinerary
        finally:
            sync_session.close()

        # Guardar la respuesta del agente
        agent_message = IAChat(
            user_id=chat_request.user_id,
            group_id=chat_request.group_id,
            message=agent_response
        )
        db.add(agent_message)
        await db.flush()
        
        # Commit todos los cambios
        await db.commit()

        return ChatResponse(
            id=agent_message.id,
            message=agent_message.message,
            created_at=agent_message.created_at,
            user_id=agent_message.user_id,
            group_id=agent_message.group_id,
            trip_id=trip.id
        )
            
    except Exception as e:
        await db.rollback()
        # Debug: Imprimir el error completo
        import traceback
        print("=== Error Detallado ===")
        print(traceback.format_exc())
        print("=====================")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el mensaje: {str(e)}"
        )
