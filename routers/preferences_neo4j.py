# routers/preferences.py
from fastapi import APIRouter
from neo4j_client import Neo4jClient

router = APIRouter()
neo4j_client = Neo4jClient()

@router.get("/preferences/users")
def obtener_preferencias_usuarios():
    query = """
    MATCH (u:User)-[r]->(p:Preference)
    WHERE type(r) STARTS WITH 'HAS_PREFERENCE_'
    RETURN
      u.name AS Usuario,
      collect(CASE WHEN type(r) = 'HAS_PREFERENCE_DESTINATION' THEN p.name ELSE null END) AS Destinos,
      collect(CASE WHEN type(r) = 'HAS_PREFERENCE_ACTIVITIES' THEN p.name ELSE null END) AS Actividades,
      collect(CASE WHEN type(r) = 'HAS_PREFERENCE_PRICE' THEN p.name ELSE null END) AS Precios,
      collect(CASE WHEN type(r) = 'HAS_PREFERENCE_ACCOMMODATION' THEN p.name ELSE null END) AS Alojamientos,
      collect(CASE WHEN type(r) = 'HAS_PREFERENCE_TRASNPORT' THEN p.name ELSE null END) AS Transportes,
      collect(CASE WHEN type(r) = 'HAS_PREFERENCE_MOTIVATION' THEN p.name ELSE null END) AS Motivaciones
    """
    try:
        resultados = neo4j_client.run_query(query)
        return resultados
    except Exception as e:
        return {"error": str(e)}
