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
from ai_agent.models import TripContext, UserPreferences, ChatMessage
from app.services.agent_preferences_service import AgentPreferencesService
from pydantic import BaseModel
from datetime import datetime
import groq
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.sql import select
from app.models.ia_chat import IAChat
from app.models.group import Group
from app.models.user import User
from app.models.group_chat import GroupChat
from app.models.trip import Trip
from app.models.itinerary import Itinerary
from dotenv import load_dotenv, dotenv_values
import os
import httpx

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

async def get_group_preferences_for_agent(group_id: uuid.UUID, db: AsyncSession) -> List[UserPreferences]:
    """
    Obtiene las preferencias de los usuarios del grupo para el agente
    """
    try:
        # Obtener preferencias desde Neo4j
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://hstp4bpv-8000.usw3.devtunnels.ms/preferences/group/{group_id}"
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error obteniendo preferencias del grupo"
                )
            
            preferences_data = response.json()
            return AgentPreferencesService.transform_preferences_to_agent_format(preferences_data)
            
    except Exception as e:
        print(f"Error obteniendo preferencias: {str(e)}")
        # Retornar lista vacía si hay error
        return []

async def create_or_get_trip(group_id: uuid.UUID, db: AsyncSession) -> Trip:
    """
    Crea un nuevo viaje o obtiene uno existente para el grupo
    """
    # Buscar si ya existe un viaje activo para este grupo
    stmt = select(Trip).where(
        Trip.group_id == group_id,
        Trip.status == True
    )
    result = await db.execute(stmt)
    existing_trip = result.scalar_one_or_none()
    
    if existing_trip:
        return existing_trip
    
    # Crear nuevo viaje
    new_trip = Trip(
        group_id=group_id,
        destination="",  # Se actualizará cuando se genere el itinerario
        start_date=None,  # Se actualizará cuando se genere el itinerario
        end_date=None,    # Se actualizará cuando se genere el itinerario
        status=True
    )
    db.add(new_trip)
    await db.flush()
    await db.refresh(new_trip)
    return new_trip

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

@router.post("/send-message", response_model=ChatResponse)
async def send_message_to_agent(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Envía un mensaje al agente y obtiene su respuesta usando el TripPlannerAgent especializado.
    """
    try:
        # Validar que el usuario y grupo existan
        is_valid = await validate_user_and_group(db, chat_request.user_id, chat_request.group_id)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="El usuario no pertenece al grupo o el grupo no existe"
            )

        # Guardar el mensaje del usuario
        user_message = IAChat(
            user_id=chat_request.user_id,
            group_id=chat_request.group_id,
            message=chat_request.message
        )
        db.add(user_message)
        await db.flush()
        
        # Obtener mensajes del chat para el contexto
        stmt = select(IAChat).where(
            IAChat.group_id == chat_request.group_id,
            IAChat.status == True
        ).order_by(IAChat.created_at.desc()).limit(10)
        result = await db.execute(stmt)
        chat_history = result.scalars().all()

        # Crear o obtener el viaje para este grupo
        trip = await create_or_get_trip(chat_request.group_id, db)
        
        # Obtener preferencias de los usuarios del grupo
        user_profiles = await get_group_preferences_for_agent(chat_request.group_id, db)
        
        # Convertir el historial de chat al formato que espera el agente
        chat_messages = [
            ChatMessage(
                user_id=msg.user_id,
                message=msg.message,
                created_at=msg.created_at
            ) for msg in chat_history
        ]
        
        # Crear el contexto para el agente
        context = TripContext(
            group_id=chat_request.group_id,
            participants=user_profiles,
            chat_history=chat_messages,
            specific_requirements=chat_request.message  # Usar el mensaje actual como requerimiento específico
        )
        
        # Crear una sesión síncrona para el agente
        sync_db = SyncSessionLocal()
        
        try:
            # Inicializar y usar el agente especializado
            agent = TripPlannerAgent(db=sync_db)
            response = agent.generate_itinerary(context=context, trip_id=trip.id)
            
            # Guardar la respuesta del agente
            agent_message = IAChat(
                user_id=chat_request.user_id,
                group_id=chat_request.group_id,
                message=response.itinerary
            )
            db.add(agent_message)
            await db.flush()
            await db.commit()
            
            return ChatResponse(
                id=agent_message.id,
                message=agent_message.message,
                created_at=agent_message.created_at,
                user_id=agent_message.user_id,
                group_id=agent_message.group_id
            )
            
        finally:
            sync_db.close()
            
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

@router.get("/itinerary/{group_id}")
async def get_group_itinerary(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el itinerario guardado para un grupo
    """
    try:
        # Buscar el viaje activo del grupo
        stmt = select(Trip).where(
            Trip.group_id == group_id,
            Trip.status == True
        )
        result = await db.execute(stmt)
        trip = result.scalar_one_or_none()
        
        if not trip:
            raise HTTPException(
                status_code=404,
                detail="No se encontró un viaje activo para este grupo"
            )
        
        # Obtener itinerario del viaje
        stmt = select(Itinerary).where(
            Itinerary.trip_id == trip.id,
            Itinerary.status == True
        ).order_by(Itinerary.day, Itinerary.start_time)
        result = await db.execute(stmt)
        itineraries = result.scalars().all()
        
        # Obtener vuelos del viaje
        from app.models.flight import Flight
        stmt = select(Flight).where(
            Flight.trip_id == trip.id,
            Flight.status == True
        )
        result = await db.execute(stmt)
        flights = result.scalars().all()
        
        # Obtener hoteles del viaje
        from app.models.hotel import Hotel
        stmt = select(Hotel).where(
            Hotel.trip_id == trip.id,
            Hotel.status == True
        )
        result = await db.execute(stmt)
        hotels = result.scalars().all()
        
        # Formatear respuesta
        itinerary_data = {
            "trip": {
                "id": str(trip.id),
                "destination": trip.destination,
                "start_date": trip.start_date.isoformat() if trip.start_date else None,
                "end_date": trip.end_date.isoformat() if trip.end_date else None,
                "created_at": trip.created_at.isoformat()
            },
            "itinerary": [
                {
                    "id": str(item.id),
                    "day": item.day.isoformat(),
                    "activity": item.activity,
                    "location": item.location,
                    "start_time": item.start_time.isoformat() if item.start_time else None,
                    "end_time": item.end_time.isoformat() if item.end_time else None
                }
                for item in itineraries
            ],
            "flights": [
                {
                    "id": str(flight.id),
                    "airline": flight.airline,
                    "departure_airport": flight.departure_airport,
                    "arrival_airport": flight.arrival_airport,
                    "departure_time": flight.departure_time.isoformat(),
                    "arrival_time": flight.arrival_time.isoformat(),
                    "price": float(flight.price) if flight.price else None
                }
                for flight in flights
            ],
            "hotels": [
                {
                    "id": str(hotel.id),
                    "name": hotel.name,
                    "location": hotel.location,
                    "price_per_night": float(hotel.price_per_night) if hotel.price_per_night else None,
                    "rating": float(hotel.rating) if hotel.rating else None,
                    "link": hotel.link
                }
                for hotel in hotels
            ]
        }
        
        return itinerary_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo el itinerario: {str(e)}"
        )
