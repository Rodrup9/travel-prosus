# routers/preferences.py
from fastapi import APIRouter, Query, HTTPException, Depends
from app.models.preferences import UserPreferenceResponse
from typing import List, Optional
import uuid
from app.services.preference_service import PreferenceService
from app.services.user import UserService
from app.neo4j_client import Neo4jClient
from app.models.preference import PreferencesModel
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
import textwrap
from app.middleware.verify_session import get_verify_session


router = APIRouter()
preference_service = PreferenceService()
neo4j_client = Neo4jClient()

@router.get("/preferences/user/{user_id}", response_model=UserPreferenceResponse)
async def obtener_preferencias_usuario(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener las preferencias de un usuario específico.
    
    Args:
        user_id: ID del usuario del cual obtener las preferencias
        
    Returns:
        UserPreferenceResponse: Respuesta con las preferencias del usuario
    """
    try:
        # Verificar que el usuario existe
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró el usuario con ID: {user_id}"
            )
        
        print(f"Buscando preferencias para usuario: {user.name} con ID: {user.id}")
        
        # Consultar preferencias en Neo4j usando el SQL ID del usuario
        user_ids = [str(user.id)]
        print(f"User IDs para consulta: {user_ids}")
        
        preferences_response = await preference_service.get_preferences(user_ids)
        
        print(f"Respuesta de preferencias: {preferences_response}")
        
        return preferences_response
        
    except Exception as e:
        print(f"Error en obtener_preferencias_usuario: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener preferencias del usuario: {str(e)}"
        )

@router.get("/preferences/users", response_model=UserPreferenceResponse)
async def obtener_preferencias_usuarios(
    group_id: uuid.UUID = Query(..., description="ID del grupo para obtener preferencias de todos sus usuarios"),
    db: AsyncSession = Depends(get_db)
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
        users_in_group = await UserService.get_user_by_group_id(db, group_id)
        
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
async def create_preferences_user(data:PreferencesModel,current_user = Depends(get_verify_session),db: AsyncSession = Depends(get_db)):
    """
    Create prefereces for a user
    Args:
        user_id: ID of the user
        preference_type: Type of preference
        preference_value: Value of the preference
    Returns:
        array of preferences
    """
    user = await UserService.get_user_by_id(db,current_user.id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found"
        )
    
    parts = []

    parts.append(textwrap.dedent(f"""
        MERGE ({user.name}:User {{id:'u{user.id}', name:'{user.name.capitalize()}'}})
        WITH {user.name}
    """).strip())

    index = 1
    for preference in data.preferences:
        parts.append(textwrap.dedent(f"""
            MERGE (p{index}:Preference {{name: '{preference.name}'}})
            MERGE ({user.name})-[:HAS_PREFERENCE_{preference.type}]->(p{index})
            WITH {user.name}
        """).strip())
        index += 1

    parts.append(textwrap.dedent(f"""
        MERGE (ID_SQL:id {{name: '{user.id}'}})
        MERGE ({user.name})-[:ID_SQL]->(ID_SQL);
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

@router.get("/preferences/debug/neo4j/{user_id}")
async def debug_neo4j_data(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Endpoint de debug para verificar qué datos hay en Neo4j para un usuario específico
    """
    try:
        # Verificar que el usuario existe
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró el usuario con ID: {user_id}"
            )
        
        print(f"Debug para usuario: {user.name} con ID: {user.id}")
        
        # Consulta simple para ver el usuario específico
        query_user = """
        MATCH (u:User)
        WHERE u.id = $user_neo4j_id
        RETURN u.id AS user_id, u.name AS user_name
        """
        
        # Consulta para ver la relación ID_SQL del usuario específico
        query_relations = """
        MATCH (u:User)-[:ID_SQL]->(sql:id)
        WHERE u.id = $user_neo4j_id
        RETURN u.id AS user_id, u.name AS user_name, sql.name AS sql_id
        """
        
        # Consulta para ver las preferencias del usuario específico
        query_preferences = """
        MATCH (u:User)-[r]->(p:Preference)
        WHERE u.id = $user_neo4j_id AND type(r) STARTS WITH 'HAS_PREFERENCE_'
        RETURN u.id AS user_id, u.name AS user_name, type(r) AS relation_type, p.name AS preference_name
        """
        
        # Consulta completa similar al endpoint de grupo pero para un usuario específico
        query_complete = """
        MATCH (u:User)-[:ID_SQL]->(sql:id {name: $user_sql_id})
        OPTIONAL MATCH (u)-[r]->(p:Preference)
        WHERE type(r) STARTS WITH 'HAS_PREFERENCE_'
        RETURN
          u.id AS user_id,
          u.name AS Usuario,
          sql.name AS sql_id,
          [x IN collect(DISTINCT CASE WHEN type(r) = 'HAS_PREFERENCE_DESTINATION' THEN p.name ELSE null END) WHERE x IS NOT NULL] AS Destinos,
          [x IN collect(DISTINCT CASE WHEN type(r) = 'HAS_PREFERENCE_ACTIVITIES' THEN p.name ELSE null END) WHERE x IS NOT NULL] AS Actividades,
          [x IN collect(DISTINCT CASE WHEN type(r) = 'HAS_PREFERENCE_PRICE' THEN p.name ELSE null END) WHERE x IS NOT NULL] AS Precios,
          [x IN collect(DISTINCT CASE WHEN type(r) = 'HAS_PREFERENCE_ACCOMMODATION' THEN p.name ELSE null END) WHERE x IS NOT NULL] AS Alojamientos,
          [x IN collect(DISTINCT CASE WHEN type(r) = 'HAS_PREFERENCE_TRASNPORT' THEN p.name ELSE null END) WHERE x IS NOT NULL] AS Transportes,
          [x IN collect(DISTINCT CASE WHEN type(r) = 'HAS_PREFERENCE_MOTIVATION' THEN p.name ELSE null END) WHERE x IS NOT NULL] AS Motivaciones
        """
        
        # Parámetros para las consultas
        user_neo4j_id = f"u{user.id}"
        user_sql_id = str(user.id)
        
        user_result = neo4j_client.run_query(query_user, {"user_neo4j_id": user_neo4j_id})
        relations_result = neo4j_client.run_query(query_relations, {"user_neo4j_id": user_neo4j_id})
        preferences_result = neo4j_client.run_query(query_preferences, {"user_neo4j_id": user_neo4j_id})
        complete_result = neo4j_client.run_query(query_complete, {"user_sql_id": user_sql_id})
        
        return {
            "user_info": {
                "sql_id": str(user.id),
                "neo4j_id": user_neo4j_id,
                "name": user.name
            },
            "user_in_neo4j": user_result,
            "relations": relations_result,
            "preferences": preferences_result,
            "complete_query_result": complete_result
        }
        
    except Exception as e:
        print(f"Error en debug: {str(e)}")
        return {"error": str(e)}
