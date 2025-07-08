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
        print(f"🔍 Iniciando búsqueda de preferencias para usuario: {user_id}")
        
        # Verificar que el usuario existe con timeout rápido
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró el usuario con ID: {user_id}"
            )
        
        print(f"✅ Usuario encontrado: {user.name} con ID: {user.id}")
        
        # Consultar preferencias en Neo4j con timeout
        user_ids = [str(user.id)]
        print(f"🔗 Consultando Neo4j para user IDs: {user_ids}")
        
        # Agregar timeout y manejo de errores específico para Neo4j
        import asyncio
        try:
            preferences_response = await asyncio.wait_for(
                preference_service.get_preferences(user_ids),
                timeout=10.0  # 10 segundos de timeout
            )
            print(f"✅ Respuesta de Neo4j recibida: {preferences_response}")
            return preferences_response
            
        except asyncio.TimeoutError:
            print("⏰ Timeout en consulta Neo4j")
            raise HTTPException(
                status_code=408, 
                detail="Timeout al consultar preferencias en Neo4j. La consulta tardó más de 10 segundos."
            )
        except Exception as neo4j_error:
            print(f"❌ Error en Neo4j: {str(neo4j_error)}")
            # Retornar respuesta vacía en caso de error de Neo4j
            return {
                "status": "error",
                "message": f"Error en Neo4j: {str(neo4j_error)}",
                "data": [],
                "user_count": 0
            }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error general en obtener_preferencias_usuario: {str(e)}")
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
        
    Example:
        GET /preferences/users?group_id=123e4567-e89b-12d3-a456-426614174000
    """
    try:
        print(f"🔍 Solicitando preferencias para grupo: {group_id}")
        
        # Validar que group_id sea un UUID válido
        if not group_id:
            raise HTTPException(
                status_code=422, 
                detail="El parámetro group_id es requerido y debe ser un UUID válido"
            )
        
        # Obtener todos los usuarios del grupo usando UserService
        users_in_group = await UserService.get_user_by_group_id(db, group_id)
        
        if not users_in_group:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontraron usuarios en el grupo con ID: {group_id}"
            )
        
        print(f"✅ Usuarios encontrados en el grupo: {len(users_in_group)}")
        
        # Extraer los IDs de los usuarios para consultar en Neo4j
        user_ids = [str(user.id) for user in users_in_group]
        print(f"🔗 User IDs para consulta Neo4j: {user_ids}")
        
        # Consultar preferencias en Neo4j con timeout
        import asyncio
        try:
            preferences_response = await asyncio.wait_for(
                preference_service.get_preferences(user_ids),
                timeout=15.0  # 15 segundos de timeout para múltiples usuarios
            )
            print(f"✅ Respuesta de preferencias de grupo: {preferences_response}")
            return preferences_response
            
        except asyncio.TimeoutError:
            print("⏰ Timeout en consulta Neo4j para grupo")
            raise HTTPException(
                status_code=408, 
                detail="Timeout al consultar preferencias del grupo en Neo4j. La consulta tardó más de 15 segundos."
            )
        except Exception as neo4j_error:
            print(f"❌ Error en Neo4j para grupo: {str(neo4j_error)}")
            # Retornar respuesta vacía en caso de error de Neo4j
            return {
                "status": "error",
                "message": f"Error en Neo4j para grupo: {str(neo4j_error)}",
                "data": [],
                "user_count": len(users_in_group)
            }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions para mantener el status code correcto
        raise he
    except Exception as e:
        print(f"❌ Error general en obtener_preferencias_usuarios: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener preferencias del grupo: {str(e)}"
        )


@router.post("/preferences/users")
async def create_preferences_user(data:PreferencesModel,current_user = Depends(get_verify_session),db: AsyncSession = Depends(get_db)):
    """
    Create preferences for a user
    Args:
        data: JSON with user preferences from frontend
        current_user: Authenticated user session
        db: Database session
    Returns:
        JSON response with the original data plus operation result
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
        # Ejecutar la consulta Neo4j
        neo4j_result = neo4j_client.run_query(query)
        print(neo4j_result)
        
        # Retornar el JSON original del frontend junto con información adicional
        return {
            "success": True,
            "message": "Preferences created successfully",
            "user_info": {
                "user_id": str(user.id),
                "user_name": user.name,
                "user_email": user.email
            },
            "received_data": {
                "preferences": [
                    {
                        "name": pref.name,
                        "type": pref.type
                    } for pref in data.preferences
                ]
            },
            "neo4j_operation": {
                "status": "completed",
                "result": neo4j_result
            }
        }
    except Exception as e:
        print(e)
        # En caso de error, también retornar el JSON original
        return {
            "success": False,
            "message": "Error creating preferences",
            "error": str(e),
            "user_info": {
                "user_id": str(user.id),
                "user_name": user.name,
                "user_email": user.email
            },
            "received_data": {
                "preferences": [
                    {
                        "name": pref.name,
                        "type": pref.type
                    } for pref in data.preferences
                ]
            },
            "neo4j_operation": {
                "status": "failed",
                "error": str(e)
            }
        }

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

@router.get("/preferences/test/neo4j")
async def test_neo4j_connection():
    """
    Test rápido de conectividad con Neo4j
    """
    try:
        import asyncio
        import time
        
        start_time = time.time()
        print("🧪 Iniciando test de conectividad Neo4j...")
        
        # Consulta simple y rápida
        simple_query = "RETURN 'Neo4j Connection OK' AS status, datetime() AS timestamp"
        
        result = await asyncio.wait_for(
            asyncio.to_thread(neo4j_client.run_query, simple_query),
            timeout=5.0  # 5 segundos de timeout
        )
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # en milisegundos
        
        print(f"✅ Neo4j conectado en {response_time}ms")
        
        return {
            "status": "success",
            "message": "Neo4j connection successful",
            "response_time_ms": response_time,
            "result": result,
            "timestamp": time.time()
        }
        
    except asyncio.TimeoutError:
        print("❌ Timeout en test Neo4j")
        return {
            "status": "timeout",
            "message": "Neo4j connection timeout after 5 seconds",
            "response_time_ms": 5000,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"❌ Error en test Neo4j: {str(e)}")
        return {
            "status": "error",
            "message": f"Neo4j connection failed: {str(e)}",
            "timestamp": time.time()
        }

@router.get("/preferences/test/preference-service")
async def test_preference_service():
    """
    Test del servicio de preferencias con datos de prueba
    """
    try:
        import asyncio
        import time
        
        start_time = time.time()
        print("🧪 Iniciando test del servicio de preferencias...")
        
        # Test con un array vacío primero
        empty_result = await asyncio.wait_for(
            preference_service.get_preferences([]),
            timeout=5.0
        )
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        print(f"✅ Servicio de preferencias respondió en {response_time}ms")
        
        return {
            "status": "success",
            "message": "Preference service working",
            "response_time_ms": response_time,
            "empty_query_result": empty_result,
            "timestamp": time.time()
        }
        
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "message": "Preference service timeout after 5 seconds",
            "response_time_ms": 5000,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"❌ Error en test servicio: {str(e)}")
        return {
            "status": "error",
            "message": f"Preference service failed: {str(e)}",
            "timestamp": time.time()
        }
