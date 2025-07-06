from typing import List, Optional
from neo4j_client import Neo4jClient
from models.preferences import UserPreferenceBase, UserPreferenceResponse

class PreferenceService:
    def __init__(self):
        self.neo4j = Neo4jClient()

    def _build_query(self, sql_ids: Optional[List[str]] = None) -> tuple[str, dict]:
        query = """
        MATCH (u:User)-[:ID_SQL]->(sql:id)
        """
        
        params = {}
        if sql_ids:
            query += " WHERE sql.name IN $sql_ids "
            params["sql_ids"] = sql_ids
        
        query += """
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
        
        return query, params

    async def get_preferences(self, sql_ids: Optional[List[str]] = None) -> UserPreferenceResponse:
        query, params = self._build_query(sql_ids)
        results = self.neo4j.run_query(query, params)
        
        if not results:
            return UserPreferenceResponse(data=[], count=0)
        
        validated_data = [UserPreferenceBase(**item) for item in results]
        return UserPreferenceResponse(data=validated_data, count=len(validated_data))