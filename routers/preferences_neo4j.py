# routers/preferences.py
from fastapi import APIRouter
from neo4j_client import Neo4jClient
from models.preference import PreferencesModel
import textwrap
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