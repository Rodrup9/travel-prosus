# 👨‍💻 Guía para Desarrolladores - Travel Prosus

## 📖 Documentación Técnica Detallada

Esta guía proporciona información técnica detallada para desarrolladores que trabajen con Travel Prosus.

## 🏗️ Estructura del Proyecto

```
travel-prosus/
├── 📁 ai_agent/                    # Módulo de Inteligencia Artificial
│   ├── __init__.py
│   ├── agent_service.py           # Servicio principal del agente IA
│   ├── config.py                  # Configuración del agente
│   ├── models.py                  # Modelos de datos para IA
│   ├── travel_service.py          # Servicios de viaje
│   ├── travel_tools.py            # Herramientas de búsqueda
│   └── test_connection.py         # Tests de conexión
├── 📁 app/                        # Aplicación principal FastAPI
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada de la aplicación
│   ├── config.py                  # Configuración global
│   ├── database.py                # Configuración de base de datos
│   ├── neo4j_client.py           # Cliente Neo4j
│   ├── supabaseClient.py         # Cliente Supabase
│   ├── 📁 middleware/             # Middleware personalizado
│   │   └── verify_session.py      # Verificación de sesiones
│   ├── 📁 models/                 # Modelos de datos SQLModel
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── trip.py
│   │   ├── flight.py
│   │   ├── hotel.py
│   │   ├── itinerary.py
│   │   ├── group_member.py
│   │   ├── group_chat.py
│   │   ├── ia_chat.py
│   │   ├── vote.py
│   │   └── preference.py
│   ├── 📁 routers/                # Rutas de API
│   │   ├── auth.py                # Autenticación
│   │   ├── users.py               # Gestión de usuarios
│   │   ├── groups.py              # Gestión de grupos
│   │   ├── trips.py               # Gestión de viajes
│   │   ├── flights.py             # Gestión de vuelos
│   │   ├── hotels.py              # Gestión de hoteles
│   │   ├── itineraries.py         # Gestión de itinerarios
│   │   ├── group_members.py       # Miembros de grupo
│   │   ├── group_chat.py          # Chat de grupo
│   │   ├── ia_chat.py             # Chat con IA
│   │   ├── votes.py               # Sistema de votación
│   │   ├── preferences_neo4j.py   # Preferencias en Neo4j
│   │   ├── websocket_chat.py      # WebSocket para chat
│   │   └── agent_preferences.py   # Preferencias del agente
│   ├── 📁 schemas/                # Esquemas Pydantic
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── group.py
│   │   ├── trip.py
│   │   ├── flight.py
│   │   ├── hotel.py
│   │   ├── itinerary.py
│   │   ├── group_member.py
│   │   ├── group_chat.py
│   │   ├── ia_chat.py
│   │   └── vote.py
│   └── 📁 services/               # Lógica de negocio
│       ├── user.py
│       ├── group.py
│       ├── trip.py
│       ├── flight.py
│       ├── hotel.py
│       ├── itinerary.py
│       ├── group_member.py
│       ├── group_chat.py
│       ├── ia_chat.py
│       ├── vote.py
│       ├── preference_service.py
│       ├── chat_service.py
│       ├── realtime_chat.py
│       └── agent_preferences_service.py
├── 📁 docs/                       # Documentación
│   └── realtime_chat_guide.md
├── 📄 requirements.txt            # Dependencias Python
├── 📄 .env                        # Variables de entorno
├── 📄 env.example                 # Ejemplo de variables de entorno
├── 📄 start_server.py             # Script de inicio
├── 📄 start_server.ps1            # Script PowerShell
├── 📄 test_server.py              # Script de testing
├── 📄 cors_test.html              # Test de CORS
├── 📄 CORS_SOLUTION.md            # Solución de problemas CORS
└── 📄 README.md                   # Documentación principal
```

## 🔧 Configuración de Desarrollo

### 1. Configuración del Entorno

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/travel-prosus.git
cd travel-prosus

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (macOS/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de desarrollo (opcional)
pip install pytest pytest-asyncio httpx black flake8 mypy
```

### 2. Configuración de Variables de Entorno

```env
# .env
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/travel_prosus
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Neo4j
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# APIs externas
AMADEUS_API_KEY=your-amadeus-key
AMADEUS_API_SECRET=your-amadeus-secret
GROQ_API_KEY=your-groq-key

# Configuración del agente IA
MODEL_NAME=llama-3.1-8b-instant
MAX_TOKENS=4096
TEMPERATURE=0.7
TOOLS_ENABLED=true
JSON_MODE=true
```

### 3. Configuración de Base de Datos

```python
# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import os

# Configuración del motor de base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Para debugging
    future=True,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Configuración de la sesión
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## 🤖 Módulo de Inteligencia Artificial

### Estructura del Agente IA

```python
# ai_agent/agent_service.py
from groq import Groq
from .config import GroqSettings
from .travel_tools import TravelPriceSearcher

class AgentService:
    def __init__(self):
        self.settings = GroqSettings()
        self.client = Groq(api_key=self.settings.GROQ_API_KEY)
        self.travel_searcher = TravelPriceSearcher(
            api_key=self.settings.AMADEUS_API_KEY,
            api_secret=self.settings.AMADEUS_API_SECRET
        )
    
    async def process_message(self, message: str, context: dict = None):
        """Procesar mensaje del usuario y generar respuesta"""
        
    async def search_flights(self, **kwargs):
        """Buscar vuelos usando Amadeus API"""
        
    async def search_hotels(self, **kwargs):
        """Buscar hoteles usando Amadeus API"""
        
    async def get_recommendations(self, user_preferences: dict):
        """Obtener recomendaciones basadas en preferencias"""
```

### Herramientas de Búsqueda

```python
# ai_agent/travel_tools.py
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class FlightPrice:
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str]
    price: float
    currency: str
    airline: str

class TravelPriceSearcher:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.amadeus.com"
        self.access_token = None
    
    async def get_access_token(self):
        """Obtener token de acceso de Amadeus"""
        
    async def search_flights(self, origin: str, destination: str, 
                           departure_date: str, **kwargs) -> List[FlightPrice]:
        """Buscar vuelos"""
        
    async def search_hotels(self, destination: str, 
                          check_in: str, check_out: str, **kwargs):
        """Buscar hoteles"""
```

## 💬 Sistema de Chat en Tiempo Real

### Configuración WebSocket

```python
# app/routers/websocket_chat.py
from fastapi import WebSocket, WebSocketDisconnect
from app.services.realtime_chat import RealtimeChatManager

router = APIRouter()
chat_manager = RealtimeChatManager()

@router.websocket("/ws/chat/{group_id}")
async def websocket_chat(websocket: WebSocket, group_id: str):
    await chat_manager.connect(websocket, group_id)
    try:
        while True:
            data = await websocket.receive_text()
            await chat_manager.handle_message(data, group_id)
    except WebSocketDisconnect:
        await chat_manager.disconnect(websocket, group_id)
```

### Gestor de Chat

```python
# app/services/realtime_chat.py
from fastapi import WebSocket
from typing import Dict, List
import json

class RealtimeChatManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, group_id: str):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = []
        self.active_connections[group_id].append(websocket)
    
    async def disconnect(self, websocket: WebSocket, group_id: str):
        if group_id in self.active_connections:
            self.active_connections[group_id].remove(websocket)
    
    async def send_message(self, message: dict, group_id: str):
        if group_id in self.active_connections:
            for connection in self.active_connections[group_id]:
                await connection.send_text(json.dumps(message))
    
    async def handle_message(self, data: str, group_id: str):
        message = json.loads(data)
        await self.send_message(message, group_id)
```

## 📊 Integración con Neo4j

### Cliente Neo4j

```python
# app/neo4j_client.py
from neo4j import AsyncGraphDatabase
from typing import List, Dict, Any
import os

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE")
        self.driver = None
    
    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(
            self.uri, 
            auth=(self.username, self.password)
        )
    
    async def close(self):
        if self.driver:
            await self.driver.close()
    
    async def execute_query(self, query: str, parameters: Dict = None):
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, parameters)
            return [record async for record in result]
```

### Servicio de Preferencias

```python
# app/services/preference_service.py
from app.neo4j_client import Neo4jClient
from typing import List, Dict
import uuid

class PreferenceService:
    def __init__(self):
        self.neo4j_client = Neo4jClient()
    
    async def get_user_preferences(self, user_id: uuid.UUID):
        """Obtener preferencias de un usuario"""
        query = """
        MATCH (u:User {id_sql: $user_id})-[:PREFERS]->(p:Preference)
        RETURN p.category, p.value, p.weight
        """
        await self.neo4j_client.connect()
        result = await self.neo4j_client.execute_query(
            query, {"user_id": str(user_id)}
        )
        await self.neo4j_client.close()
        return result
    
    async def save_user_preferences(self, user_id: uuid.UUID, preferences: List[Dict]):
        """Guardar preferencias de usuario"""
        query = """
        MERGE (u:User {id_sql: $user_id})
        WITH u
        UNWIND $preferences AS pref
        MERGE (p:Preference {category: pref.category, value: pref.value})
        MERGE (u)-[r:PREFERS]->(p)
        SET r.weight = pref.weight
        """
        await self.neo4j_client.connect()
        await self.neo4j_client.execute_query(
            query, {"user_id": str(user_id), "preferences": preferences}
        )
        await self.neo4j_client.close()
```

## 🔒 Autenticación y Seguridad

### Middleware de Autenticación

```python
# app/middleware/verify_session.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from app.supabaseClient import supabase
import jwt

security = HTTPBearer()

async def get_verify_session(token: str = Depends(security)):
    try:
        # Verificar token con Supabase
        user = supabase.auth.get_user(token.credentials)
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid authentication token"
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication token"
        )
```

### Configuración CORS

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar para producción
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

## 🧪 Testing

### Configuración de Tests

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db

# Base de datos de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)
```

### Tests de Endpoints

```python
# tests/test_users.py
import pytest
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_get_users(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Tests de WebSocket

```python
# tests/test_websocket.py
import pytest
from fastapi.testclient import TestClient

def test_websocket_chat(client: TestClient):
    with client.websocket_connect("/ws/chat/test-group") as websocket:
        data = {"type": "message", "content": "Hello", "user_id": "test-user"}
        websocket.send_json(data)
        response = websocket.receive_json()
        assert response["type"] == "message"
        assert response["content"] == "Hello"
```

## 📈 Monitoreo y Logging

### Configuración de Logs

```python
# app/config.py
import logging
from typing import Optional

def setup_logging(log_level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Configurar loggers específicos
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
```

### Health Checks

```python
# app/routers/health.py
from fastapi import APIRouter
from app.database import engine
from app.neo4j_client import Neo4jClient

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        # Verificar conexión a PostgreSQL
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # Verificar conexión a Neo4j
        neo4j_client = Neo4jClient()
        await neo4j_client.connect()
        await neo4j_client.execute_query("RETURN 1")
        await neo4j_client.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "neo4j": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## 🚀 Despliegue

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - NEO4J_URI=${NEO4J_URI}
      - NEO4J_USERNAME=${NEO4J_USERNAME}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - AMADEUS_API_KEY=${AMADEUS_API_KEY}
      - AMADEUS_API_SECRET=${AMADEUS_API_SECRET}
    depends_on:
      - postgres
      - neo4j

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=travel_prosus
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  neo4j:
    image: neo4j:5.19
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

volumes:
  postgres_data:
  neo4j_data:
```

## 🔧 Herramientas de Desarrollo

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.961
    hooks:
      - id: mypy
```

### Makefile

```makefile
.PHONY: install run test lint format clean

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	flake8 app/ ai_agent/
	mypy app/ ai_agent/

format:
	black app/ ai_agent/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache

docker-build:
	docker build -t travel-prosus .

docker-run:
	docker-compose up -d

docker-logs:
	docker-compose logs -f app
```

## 📚 Recursos Adicionales

### Documentación de APIs

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Amadeus API Documentation](https://developers.amadeus.com/)
- [Neo4j Driver Documentation](https://neo4j.com/docs/api/python-driver/)
- [Supabase Python Documentation](https://supabase.com/docs/reference/python)

### Ejemplos de Uso

```python
# Ejemplo completo de uso del sistema
async def example_usage():
    # 1. Crear usuario
    user = await UserService.create_user(
        username="johndoe",
        email="john@example.com",
        name="John Doe"
    )
    
    # 2. Crear grupo
    group = await GroupService.create_group(
        name="Viaje a París",
        description="Viaje de fin de semana",
        created_by=user.id
    )
    
    # 3. Agregar miembro al grupo
    await GroupMemberService.add_member(group.id, user.id)
    
    # 4. Buscar vuelos con IA
    agent = AgentService()
    flights = await agent.search_flights(
        origin="MAD",
        destination="CDG",
        departure_date="2024-12-01"
    )
    
    # 5. Guardar preferencias
    await PreferenceService.save_user_preferences(
        user.id,
        [{"category": "accommodation", "value": "hotel", "weight": 0.8}]
    )
```

Esta documentación proporciona una guía completa para desarrolladores que trabajen con Travel Prosus. Mantén este archivo actualizado a medida que el proyecto evolucione.
