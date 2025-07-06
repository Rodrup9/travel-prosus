# routers/preferences.py
from fastapi import APIRouter, Query, HTTPException, Depends
from app.models.preferences import UserPreferenceResponse
from typing import List, Optional
import uuid
import app.neo4j_client as neo4j_client
from app.services.preference_service import PreferenceService
from app.services.user import UserService
from app.neo4j_client import Neo4jClient
from app.models.preference import PreferencesModel
from app.database import get_db
from sqlalchemy.orm import Session
import textwrap



router = APIRouter()
preference_service = PreferenceService()
neo4j_client = Neo4jClient()

@router.get("/preferences/users", response_model=UserPreferenceResponse)
async def obtener_preferencias_usuarios(
    group_id: uuid.UUID = Query(..., description="ID del grupo para obtener preferencias de todos sus usuarios"),
    db: Session = Depends(get_db)
):
    """
    Obtener las preferencias de todos los usuarios de un grupo específico.
    
    Args:
        group_id: ID del grupo del cual obtener las preferencias de sus usuarios
        
    Returns:
        UserPreferenceResponse: Respuesta con las preferencias de todos los usuarios del grupo
    """
    try:
        # Obtener todos los usuarios del grupo usando UserService
        users_in_group = UserService.get_user_by_group_id(db, group_id)
        
        if not users_in_group:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron usuarios en el grupo con ID: {group_id}"
            )
        
        # Extraer los IDs de los usuarios para consultar en Neo4j
        user_ids = [str(user.id) for user in users_in_group]
        
        # Consultar preferencias en Neo4j usando los SQL IDs
        preferences_response = await preference_service.get_preferences(user_ids)
        
        return preferences_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener preferencias del grupo: {str(e)}"
        )


@router.post("/preferences/users")
def create_preferences_user(data:PreferencesModel):
    """
    Create prefereces for a user
    Args:
        user_id: ID of the user
        preference_type: Type of preference
        preference_value: Value of the preference
    Returns:
        array of preferences
    """
    parts = []

    parts.append(textwrap.dedent(f"""
        MERGE ({data.name_user}:User {{id:'u{data.user_id}', name:'{data.name_user.capitalize()}'}})
        WITH {data.name_user}
    """).strip())

    index = 1
    for preference in data.preferences:
        parts.append(textwrap.dedent(f"""
            MERGE (p{index}:Preference {{name: '{preference.name}'}})
            MERGE ({data.name_user})-[:HAS_PREFERENCE_{preference.type}]->(p{index})
            WITH {data.name_user}
        """).strip())
        index += 1

    parts.append(textwrap.dedent(f"""
        MERGE (ID_SQL:id {{name: '{data.user_id}'}})
        MERGE ({data.name_user})-[:ID_SQL]->(ID_SQL);
    """).strip())

    query = "\n".join(parts)
    print(query)

    try:
        result = neo4j_client.run_query(query)
        print(result)
        return result
    except Exception as e:
        print(e)
        return {"error": str(e)}
