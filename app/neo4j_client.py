# neo4j_client.py
from neo4j import GraphDatabase
from app.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
import time

class Neo4jClient:
    def __init__(self):
        try:
            print(f"🔗 Conectando a Neo4j: {NEO4J_URI}")
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                max_connection_lifetime=30,  # 30 segundos
                max_connection_pool_size=50,
                connection_timeout=10,  # 10 segundos timeout de conexión
                resolver=None
            )
            self.verify_connection()
        except Exception as e:
            print(f"❌ Error inicializando Neo4j client: {e}")
            raise

    def verify_connection(self):
        try:
            start_time = time.time()
            self.driver.verify_connectivity()
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            print(f"✅ Conexión a Neo4j establecida exitosamente en {response_time}ms")
        except Exception as e:
            print(f"❌ Conexión a Neo4j falló: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()
            print("🔌 Conexión Neo4j cerrada")

    def run_query(self, query: str, parameters: dict = {}):
        """
        Ejecutar consulta en Neo4j con timeout y manejo de errores mejorado
        """
        start_time = time.time()
        
        try:
            print(f"🔍 Ejecutando query Neo4j...")
            print(f"Query: {query[:100]}...")  # Solo primeros 100 caracteres
            print(f"Params: {parameters}")
            
            with self.driver.session() as session:
                result = session.run(query, parameters)
                data = [record.data() for record in result]
                
                end_time = time.time()
                response_time = round((end_time - start_time) * 1000, 2)
                
                print(f"✅ Query ejecutada en {response_time}ms, {len(data)} registros")
                return data
                
        except Exception as e:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            print(f"❌ Error en query Neo4j después de {response_time}ms: {e}")
            raise

