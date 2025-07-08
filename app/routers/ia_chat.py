from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.ia_chat import IAChatCreate, IAChatUpdate, IAChatResponse
from app.services.ia_chat import IAChatService
from app.services.travel_agent_service import TravelAgentService
from app.database import get_db
import uuid
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.sql import select
from app.models.ia_chat import IAChat
from app.models.group import Group
from app.models.user import User
from app.models.group_chat import GroupChat

router = APIRouter(prefix="/ia_chat", tags=["IA Chat"])

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
        from ai_agent.config import settings
        return {"message": "Configuración cargada correctamente", "config": {
            "MODEL_NAME": settings.MODEL_NAME,
            "TEMPERATURE": settings.TEMPERATURE,
            "MAX_TOKENS": settings.MAX_TOKENS,
            "TOOLS_ENABLED": settings.TOOLS_ENABLED,
            "WEB_SEARCH_ENABLED": settings.WEB_SEARCH_ENABLED
        }}
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return {"message": "Error cargando configuración", "error": str(e), "detail": error_detail}

@router.post("/", response_model=IAChatResponse, status_code=status.HTTP_201_CREATED)
async def create_message(chat: IAChatCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await IAChatService.create_message(db, chat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[IAChatResponse])
async def get_all_messages(db: AsyncSession = Depends(get_db)):
    return await IAChatService.get_all_messages(db)

@router.get("/{message_id}", response_model=IAChatResponse)
async def get_message_by_id(message_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    message = await IAChatService.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return message

@router.put("/{message_id}", response_model=IAChatResponse)
async def update_message(message_id: uuid.UUID, chat_update: IAChatUpdate, db: AsyncSession = Depends(get_db)):
    updated = await IAChatService.update_message(db, message_id, chat_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return updated

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await IAChatService.delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return

@router.patch("/{message_id}/toggle", response_model=IAChatResponse)
async def toggle_status(message_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    toggled = await IAChatService.toggle_status(db, message_id)
    if not toggled:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return toggled

@router.get("/user/{user_id}", response_model=List[IAChatResponse])
async def get_messages_by_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await IAChatService.get_messages_by_user(db, user_id)

@router.get("/group/{group_id}", response_model=List[IAChatResponse])
async def get_messages_by_group(group_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await IAChatService.get_messages_by_group(db, group_id)

@router.get("/user/{user_id}/group/{group_id}", response_model=List[IAChatResponse])
async def get_messages_by_user_and_group(user_id: uuid.UUID, group_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await IAChatService.get_messages_by_user_and_group(db, user_id, group_id)

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

@router.post("/send-message")
async def send_message_to_agent(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Envía un mensaje al agente y obtiene su respuesta usando el agente de viajes personalizado.
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
        
        # Crear el servicio del agente de viajes
        travel_agent_service = TravelAgentService(db=db)
        
        # Procesar el mensaje con el agente
        result = await travel_agent_service.process_message(
            user_id=chat_request.user_id,
            group_id=chat_request.group_id,
            message=chat_request.message
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error del agente: {result['error']}"
            )
        
        # Guardar la respuesta del agente
        agent_message = await travel_agent_service.save_agent_response(
            user_id=chat_request.user_id,
            group_id=chat_request.group_id,
            response=result["response"]
        )
        
        await db.commit()

        # Mejorar la presentación del mensaje para el usuario
        import re
        import json
        raw_msg = agent_message.message
        print("\n===== RESPUESTA CRUDA DEL AGENTE =====\n", raw_msg, "\n==============================\n")
        # Buscar JSON en la respuesta
        json_match = re.search(r'```json\s*([\s\S]+?)```', raw_msg)
        pretty = ""
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                # Mostrar itinerario si existe
                if "itinerary_days" in data:
                    pretty += "\n\n🗺️ **Itinerario sugerido:**\n"
                    for day in data["itinerary_days"]:
                        pretty += f"\n**Día {day.get('day', '?')}:**\n"
                        for act in day.get("activities", []):
                            pretty += f"- {act.get('activity', '')}"
                            if act.get('location'):
                                pretty += f" en {act['location']}"
                            if act.get('time'):
                                pretty += f" a las {act['time']}"
                            pretty += "\n"
                # Mostrar vuelos y hoteles si existen
                if "vuelos" in data:
                    pretty += "\n✈️ **Vuelos encontrados:**\n"
                    for vuelo in data.get("vuelos", []):
                        pretty += f"- **Origen:** {vuelo.get('origen', '-')}  |  **Destino:** {vuelo.get('destino', '-')}  |  **Precio:** {vuelo.get('precio', '-')}  |  **Aerolínea:** {vuelo.get('aerolínea', '-')}\n"
                if "hoteles" in data:
                    pretty += "\n🏨 **Hoteles encontrados:**\n"
                    for hotel in data.get("hoteles", []):
                        pretty += f"- **Ciudad:** {hotel.get('ciudad', '-')}  |  **Precio por noche:** {hotel.get('precio', '-')}\n"
                fechas = data.get("fechas", {})
                if fechas:
                    pretty += f"\n📅 **Fechas del viaje:** {fechas.get('inicio', '-')} al {fechas.get('fin', '-')}\n"
                pretty += "---\n"
            except Exception:
                pretty = ""
        # Eliminar frases técnicas y redundantes
        resumen = raw_msg
        resumen = re.sub(r'A continuación[\s\S]+?formato JSON estructurado:', '', resumen, flags=re.IGNORECASE)
        resumen = re.sub(r'A continuación[\s\S]+?en formato JSON:', '', resumen, flags=re.IGNORECASE)
        resumen = re.sub(r'La información sobre vuelos[\s\S]+?es la siguiente:', '', resumen, flags=re.IGNORECASE)
        resumen = re.sub(r'```json[\s\S]+?```', '', resumen)
        resumen = re.sub(r'\n{2,}', '\n', resumen)
        resumen = resumen.strip()
        # Si el resumen termina con una despedida, la dejamos, si no, solo mostramos la tabla bonita
        if pretty:
            despedida_match = re.search(r'(¡Disfruta tu viaje!|Espero que esta información te sea útil[\s\S]+)', resumen)
            despedida = despedida_match.group(1) if despedida_match else ''
            final_msg = f"{pretty}\n{despedida}".strip()
        else:
            final_msg = resumen
        # Limpiar saltos de línea extra
        final_msg = re.sub(r'\n{3,}', '\n\n', final_msg)
        return {"message": final_msg}
        
    except Exception as e:
        await db.rollback()
        # Debug: Imprimir el error completo
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando el mensaje: {str(e)}"
        )
