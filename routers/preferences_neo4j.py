# routers/preferences.py

from fastapi import APIRouter, Query
from models.preferences import UserPreferenceResponse
from typing import List, Optional
import neo4j_client
from servies.preference_service import PreferenceService
from neo4j_client import Neo4jClient
from models.preference import PreferencesModel
import textwrap

router = APIRouter()
preference_service = PreferenceService()

@router.get("/preferences/users", response_model=UserPreferenceResponse)
async def obtener_preferencias_usuarios(
  sql_ids: Optional[List[str]] = Query(None, description="ID O IDs de SQL a consultar")
):

    return await preference_service.get_preferences(sql_ids)

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

