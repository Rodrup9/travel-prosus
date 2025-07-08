# 👨‍💻 Developer Guide - Travel Prosus

## 📖 Detailed Technical Documentation

This guide provides detailed technical information for developers working with Travel Prosus.

## 🏗️ Project Structure

```
travel-prosus/
├── 📁 ai_agent/                    # Artificial Intelligence Module
│   ├── __init__.py
│   ├── agent_service.py           # Main AI agent service
│   ├── config.py                  # Agent configuration
│   ├── models.py                  # Data models for AI
│   ├── travel_service.py          # Travel services
│   ├── travel_tools.py            # Search tools
│   └── test_connection.py         # Connection tests
├── 📁 app/                        # Main FastAPI application
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Global configuration
│   ├── database.py                # Database configuration
│   ├── neo4j_client.py           # Neo4j client
│   ├── supabaseClient.py         # Supabase client
│   ├── 📁 middleware/             # Custom middleware
│   │   └── verify_session.py      # Session verification
│   ├── 📁 models/                 # SQLModel data models
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
│   ├── 📁 routers/                # API routes
│   │   ├── auth.py                # Authentication
│   │   ├── users.py               # User management
│   │   ├── groups.py              # Group management
│   │   ├── trips.py               # Trip management
│   │   ├── flights.py             # Flight management
│   │   ├── hotels.py              # Hotel management
│   │   ├── itineraries.py         # Itinerary management
│   │   ├── group_members.py       # Group members
│   │   ├── group_chat.py          # Group chat
│   │   ├── ia_chat.py             # AI chat
│   │   ├── votes.py               # Voting system
│   │   ├── preferences_neo4j.py   # Preferences in Neo4j
│   │   ├── websocket_chat.py      # WebSocket for chat
│   │   └── agent_preferences.py   # Agent preferences
│   ├── 📁 schemas/                # Pydantic schemas
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
│   └── 📁 services/               # Business logic
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
├── 📁 docs/                       # Documentation
│   └── realtime_chat_guide.md
├── 📄 requirements.txt            # Python dependencies
├── 📄 .env                        # Environment variables
├── 📄 env.example                 # Environment variables example
├── 📄 start_server.py             # Startup script
├── 📄 start_server.ps1            # PowerShell script
├── 📄 test_server.py              # Testing script
├── 📄 cors_test.html              # CORS test
├── 📄 CORS_SOLUTION.md            # CORS troubleshooting
└── 📄 README.md                   # Main documentation
```

## 🔧 Development Setup

### 1. Environment Configuration

```bash
# Clone repository
git clone https://github.com/your-username/travel-prosus.git
cd travel-prosus

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-asyncio httpx black flake8 mypy
```

### 2. Environment Variables Configuration

```env
# .env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/travel_prosus
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Neo4j
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# External APIs
AMADEUS_API_KEY=your-amadeus-key
AMADEUS_API_SECRET=your-amadeus-secret
GROQ_API_KEY=your-groq-key

# AI agent configuration
MODEL_NAME=llama-3.1-8b-instant
MAX_TOKENS=4096
TEMPERATURE=0.7
TOOLS_ENABLED=true
JSON_MODE=true
```

### 3. Database Configuration

```python
# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import os

# Database engine configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # For debugging
    future=True,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Session configuration
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

## 🤖 Artificial Intelligence Module

### AI Agent Structure

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
        """Process user message and generate response"""
        
    async def search_flights(self, **kwargs):
        """Search flights using Amadeus API"""
        
    async def search_hotels(self, **kwargs):
        """Search hotels using Amadeus API"""
        
    async def get_recommendations(self, user_preferences: dict):
        """Get recommendations based on preferences"""
```

### Search Tools

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
        """Get Amadeus access token"""
        
    async def search_flights(self, origin: str, destination: str, 
                           departure_date: str, **kwargs) -> List[FlightPrice]:
        """Search flights"""
        
    async def search_hotels(self, destination: str, 
                          check_in: str, check_out: str, **kwargs):
        """Search hotels"""
```

## 💬 Real-time Chat System

### WebSocket Configuration

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

### Chat Manager

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

## 📊 Neo4j Integration

### Neo4j Client

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

### Preference Service

```python
# app/services/preference_service.py
from app.neo4j_client import Neo4jClient
from typing import List, Dict
import uuid

class PreferenceService:
    def __init__(self):
        self.neo4j_client = Neo4jClient()
    
    async def get_user_preferences(self, user_id: uuid.UUID):
        """Get user preferences"""
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
        """Save user preferences"""
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

## 🔒 Authentication and Security

### Authentication Middleware

```python
# app/middleware/verify_session.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from app.supabaseClient import supabase
import jwt

security = HTTPBearer()

async def get_verify_session(token: str = Depends(security)):
    try:
        # Verify token with Supabase
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

### CORS Configuration

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)
```

## 🧪 Testing

### Test Configuration

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db

# Test database
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

### Endpoint Tests

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

### WebSocket Tests

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

## 📈 Monitoring and Logging

### Logging Configuration

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
    
    # Configure specific loggers
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
        # Check PostgreSQL connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # Check Neo4j connection
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

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
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

## 🔧 Development Tools

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

## 📚 Additional Resources

### API Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Amadeus API Documentation](https://developers.amadeus.com/)
- [Neo4j Driver Documentation](https://neo4j.com/docs/api/python-driver/)
- [Supabase Python Documentation](https://supabase.com/docs/reference/python)

### Usage Examples

```python
# Complete system usage example
async def example_usage():
    # 1. Create user
    user = await UserService.create_user(
        username="johndoe",
        email="john@example.com",
        name="John Doe"
    )
    
    # 2. Create group
    group = await GroupService.create_group(
        name="Paris Trip",
        description="Weekend trip",
        created_by=user.id
    )
    
    # 3. Add member to group
    await GroupMemberService.add_member(group.id, user.id)
    
    # 4. Search flights with AI
    agent = AgentService()
    flights = await agent.search_flights(
        origin="MAD",
        destination="CDG",
        departure_date="2024-12-01"
    )
    
    # 5. Save preferences
    await PreferenceService.save_user_preferences(
        user.id,
        [{"category": "accommodation", "value": "hotel", "weight": 0.8}]
    )
```

This documentation provides a complete guide for developers working with Travel Prosus. Keep this file updated as the project evolves.
