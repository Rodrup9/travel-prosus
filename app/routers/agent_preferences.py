from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from app.database import get_db, get_sync_db
from app.services.agent_preferences_service import AgentPreferencesService
from app.routers.preferences_neo4j import preference_service
from ai_agent.models import UserPreferences, TripContext, AgentResponse, ChatMessage
from app.services.user import UserService
from ai_agent.agent_service import TripPlannerAgent
import httpx

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)

@router.get("/group-preferences/{group_id}", response_model=List[UserPreferences])
async def get_group_preferences_for_agent(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene las preferencias de todos los usuarios de un grupo en el formato que necesita el agente.
    
    Args:
        group_id: ID del grupo del cual obtener las preferencias
        
    Returns:
        List[UserPreferences]: Lista de perfiles de usuario con sus preferencias formateadas para el agente
    """
    try:
        # Obtener todos los usuarios del grupo
        users_in_group = await UserService.get_user_by_group_id(db, group_id)
        
        if not users_in_group:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron usuarios en el grupo con ID: {group_id}"
            )
            
        # Extraer los IDs de los usuarios
        user_ids = [str(user.id) for user in users_in_group]
        
        # Obtener preferencias usando el servicio existente
        preferences = await preference_service.get_preferences(user_ids)
        
        # Transformar al formato que necesita el agente
        agent_profiles = AgentPreferencesService.transform_preferences_to_agent_format(preferences)
        
        return agent_profiles
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener preferencias para el agente: {str(e)}"
        )

@router.post("/generate-itinerary/{group_id}", response_model=AgentResponse)
async def generate_group_itinerary(
    group_id: uuid.UUID,
    specific_requirements: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Genera un itinerario para un grupo usando el agente de IA.
    
    Args:
        group_id: ID del grupo para el cual generar el itinerario
        specific_requirements: Requerimientos específicos para el itinerario (opcional)
        
    Returns:
        AgentResponse: Respuesta del agente con el itinerario generado
    """
    try:
        # Obtener preferencias de los usuarios
        user_profiles = await get_group_preferences_for_agent(group_id, db)
        
        # Obtener historial de chat del grupo
        async with httpx.AsyncClient() as client:
            chat_response = await client.get(
                f"https://hstp4bpv-8000.usw3.devtunnels.ms/group_chat/group-chat/group/{group_id}"
            )
            if chat_response.status_code != 200:
                raise HTTPException(
                    status_code=chat_response.status_code,
                    detail="Error obteniendo el historial de chat"
                )
            # Convertir los mensajes al nuevo formato ChatMessage
            chat_messages = [
                ChatMessage(
                    user_id=uuid.UUID(msg["user_id"]),
                    message=msg["message"],
                    created_at=msg["created_at"]
                ) for msg in chat_response.json()
            ]
        
        # Generar un ID único para este viaje
        trip_id = uuid.uuid4()
        
        # Crear el contexto para el agente
        context = TripContext(
            group_id=group_id,  # Ahora usamos group_id en lugar de trip_id
            participants=user_profiles,
            chat_history=chat_messages,
            specific_requirements=specific_requirements
        )
        
        # Crear una sesión síncrona
        sync_db = next(get_sync_db())
        
        try:
            # Inicializar y usar el agente
            agent = TripPlannerAgent(db=sync_db)  # Pasamos la sesión síncrona
            response = agent.generate_itinerary(context=context, trip_id=trip_id)  # Pasamos el trip_id
            return response
            
        finally:
            sync_db.close()  # Asegurarnos de cerrar la sesión síncrona
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando el itinerario: {str(e)}"
        ) 