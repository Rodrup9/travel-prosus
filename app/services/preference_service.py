from typing import List, Optional
from app.neo4j_client import Neo4jClient
from app.models.preferences import UserPreferenceBase, UserPreferenceResponse

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
        """
        Obtener preferencias de usuarios de forma asíncrona
        """
        try:
            import asyncio
            
            query, params = self._build_query(sql_ids)
            print(f"Query ejecutada: {query}")
            print(f"Parámetros: {params}")
            
            # Ejecutar la consulta en un thread separado para no bloquear
            results = await asyncio.to_thread(self.neo4j.run_query, query, params)
            print(f"Resultados de Neo4j: {results}")
            
            if not results:
                print("No se encontraron resultados")
                return UserPreferenceResponse(
                    status="success",
                    message="No preferences found",
                    data=[], 
                    user_count=0
                )
            
            validated_data = [UserPreferenceBase(**item) for item in results]
            print(f"Datos validados: {len(validated_data)} registros")
            
            return UserPreferenceResponse(
                status="success",
                message=f"Found preferences for {len(validated_data)} users",
                data=validated_data, 
                user_count=len(validated_data)
            )
            
        except Exception as e:
            print(f"Error en get_preferences: {str(e)}")
            return UserPreferenceResponse(
                status="error",
                message=f"Error getting preferences: {str(e)}",
                data=[], 
                user_count=0
            )