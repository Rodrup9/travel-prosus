from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.database import get_db
from app.services.agent_preferences_service import AgentPreferencesService
from app.routers.preferences_neo4j import preference_service
from ai_agent.models import UserProfile

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)

@router.get("/group-preferences/{group_id}", response_model=List[UserProfile])
async def get_group_preferences_for_agent(
    group_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obtiene las preferencias de todos los usuarios de un grupo en el formato que necesita el agente.
    
    Args:
        group_id: ID del grupo del cual obtener las preferencias
        
    Returns:
        List[UserProfile]: Lista de perfiles de usuario con sus preferencias formateadas para el agente
    """
    try:
        # Obtener preferencias usando el servicio existente
        preferences = await preference_service.get_preferences_usuarios(group_id, db)
        
        # Transformar al formato que necesita el agente
        agent_profiles = AgentPreferencesService.transform_preferences_to_agent_format(preferences)
        
        return agent_profiles
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener preferencias para el agente: {str(e)}"
        ) 