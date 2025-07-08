# 🌍 Travel Prosus - AI-Powered Travel Planning Platform

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j">
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=websocket&logoColor=white" alt="WebSocket">
  <img src="https://img.shields.io/badge/Groq-FF6B35?style=for-the-badge&logo=groq&logoColor=white" alt="Groq">
</div>

## 📖 Description

Travel Prosus is an advanced travel planning platform that uses artificial intelligence to create personalized travel experiences. The application combines modern technologies like FastAPI, Neo4j, Supabase, and WebSockets to offer a complete group travel planning experience.

### 🚀 Key Features

- **🤖 Intelligent AI Agent**: Uses Groq LLaMA 3.1 for personalized recommendations
- **👥 Group Planning**: Real-time collaboration between group members
- **💬 Real-time Chat**: Instant communication with WebSockets
- **✈️ Amadeus Integration**: Real-time flight and hotel search
- **📊 Preference System**: Smart storage in Neo4j
- **🗳️ Voting System**: Democratic decisions for the group
- **📱 Complete REST API**: Endpoints for all functionalities
- **🔐 Secure Authentication**: Authentication system with Supabase

## 🏗️ System Architecture

```
Travel Prosus
├── 🧠 AI Agent (Groq LLaMA 3.1)
│   ├── Personalized recommendations
│   ├── Flight/hotel search
│   └── Preference analysis
├── 🏛️ Backend (FastAPI)
│   ├── REST API
│   ├── WebSocket Chat
│   ├── Authentication
│   └── Data management
├── 📊 Databases
│   ├── PostgreSQL (Supabase) - Main data
│   └── Neo4j - Preferences and relationships
└── 🌐 External Services
    ├── Amadeus API - Flights and hotels
    ├── Supabase - Database and auth
    └── Groq - Artificial intelligence
```

## 🛠️ Technologies Used

### Backend
- **FastAPI**: Modern and fast web framework
- **SQLModel**: Asynchronous ORM for PostgreSQL
- **Supabase**: PostgreSQL database as a service
- **Neo4j**: Graph database for preferences
- **WebSockets**: Real-time communication
- **Uvicorn**: ASGI server

### AI and Services
- **Groq**: AI API with LLaMA 3.1
- **Amadeus API**: Flight and hotel search
- **Neo4j Aura**: Cloud graph database

### Development Tools
- **Python 3.12+**: Main language
- **Pydantic**: Data validation
- **python-dotenv**: Environment variable management
- **AsyncPG**: Asynchronous PostgreSQL driver

## 📋 Prerequisites

- Python 3.12 or higher
- Node.js 18+ (for frontend)
- Supabase account
- Neo4j Aura account
- Amadeus API Key
- Groq API Key

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/travel-prosus.git
cd travel-prosus
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://user:pass@host:port/database

# Amadeus API
AMADEUS_API_KEY=your-amadeus-key
AMADEUS_API_SECRET=your-amadeus-secret

# Groq AI
GROQ_API_KEY=your-groq-api-key
MODEL_NAME=llama-3.1-8b-instant
MAX_TOKENS=4096
TEMPERATURE=0.7
TOOLS_ENABLED=true
JSON_MODE=true

# Web Search Configuration
WEB_SEARCH_ENABLED=true
```

### 5. Configure Databases

#### PostgreSQL (Supabase)
1. Create a project on [Supabase](https://supabase.com)
2. Get the URL and anonymous key
3. Tables will be created automatically when starting the application

#### Neo4j
1. Create an instance on [Neo4j Aura](https://neo4j.com/aura/)
2. Get the connection credentials
3. The database will be configured automatically

### 6. Start the Server

```bash
# Option 1: Use PowerShell script (Windows)
.\start_server.ps1

# Option 2: Use uvicorn directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Use Python script
python start_server.py
```

The server will be available at `http://localhost:8000`

## 📚 API Documentation

### Main Endpoints

#### 🔐 Authentication
- `POST /auth/login` - Login
- `POST /auth/register` - Register user
- `POST /auth/logout` - Logout

#### 👥 Users
- `GET /users` - Get all users
- `GET /users/{user_id}` - Get specific user
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

#### 🏠 Groups
- `GET /groups` - Get all groups
- `GET /groups/{group_id}` - Get specific group
- `POST /groups` - Create new group
- `PUT /groups/{group_id}` - Update group
- `DELETE /groups/{group_id}` - Delete group

#### ✈️ Flights
- `GET /flights` - Get flights
- `GET /flights/{flight_id}` - Get specific flight
- `POST /flights` - Create flight
- `PUT /flights/{flight_id}` - Update flight
- `DELETE /flights/{flight_id}` - Delete flight

#### 🏨 Hotels
- `GET /hotels` - Get hotels
- `GET /hotels/{hotel_id}` - Get specific hotel
- `POST /hotels` - Create hotel
- `PUT /hotels/{hotel_id}` - Update hotel
- `DELETE /hotels/{hotel_id}` - Delete hotel

#### 🗳️ Voting
- `GET /votes` - Get votes
- `POST /votes` - Create vote
- `GET /votes/{vote_id}` - Get specific vote

#### 📊 Preferences
- `GET /preferences/user/{user_id}` - Get user preferences
- `GET /preferences/users?group_id={group_id}` - Get group preferences

### 🔍 Interactive Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤖 AI Agent

### Agent Features

The AI agent uses **Groq LLaMA 3.1** to provide:

1. **Destination Recommendations**: Based on user preferences
2. **Flight Search**: Integration with Amadeus API
3. **Hotel Search**: Personalized recommendations
4. **Preference Analysis**: Using Neo4j to store patterns
5. **Custom Itineraries**: Automatic travel plan creation

### Agent Tools

```python
# Example of agent usage
from ai_agent.agent_service import AgentService

agent = AgentService()

# Flight search
flights = await agent.search_flights(
    origin="MAD",
    destination="BCN",
    departure_date="2024-12-01",
    return_date="2024-12-05"
)

# Hotel recommendations
hotels = await agent.search_hotels(
    destination="Barcelona",
    check_in="2024-12-01",
    check_out="2024-12-05"
)
```

## 💬 Real-time Chat

### Chat Features

- **WebSocket**: Instant bidirectional communication
- **Persistence**: Messages saved in Supabase
- **Typing Indicators**: Shows when someone is typing
- **Auto-reconnection**: Handles disconnections
- **Multiple Channels**: Chat per travel group

### WebSocket Connection

```javascript
// Example connection from frontend
const ws = new WebSocket('ws://localhost:8000/ws/chat/{group_id}');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message received:', data);
};

ws.send(JSON.stringify({
    type: 'message',
    content: 'Hello group!',
    user_id: 'user-uuid'
}));
```

### Message Types

- **message**: Normal text message
- **typing**: Typing indicator
- **system**: System messages
- **ai_response**: AI agent responses

## 🧪 Testing

### Verify CORS

Open `cors_test.html` in your browser to test backend communication.

### Run Tests

```bash
# Run import tests
python test_server.py

# Test specific endpoints
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/cors-test"
```

## 📊 Data Structure

### Main Models

```python
# User
class User:
    id: UUID
    username: str
    email: str
    name: str
    created_at: datetime

# Group
class Group:
    id: UUID
    name: str
    description: str
    created_by: UUID
    created_at: datetime

# Trip
class Trip:
    id: UUID
    group_id: UUID
    destination: str
    start_date: date
    end_date: date
    budget: float
```

## 🔧 Advanced Configuration

### Customize AI Agent

```python
# In ai_agent/config.py
class GroqSettings:
    MODEL_NAME: str = "llama-3.1-8b-instant"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    TOOLS_ENABLED: bool = True
```

### Configure Neo4j

```python
# Example preference query
MATCH (u:User)-[:PREFERS]->(p:Preference)
WHERE u.id_sql = $user_id
RETURN p.category, p.value, p.weight
```

## 🚀 Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Environment Variables

```env
# CORS Configuration
CORS_ORIGINS=["https://your-domain.com", "https://www.your-domain.com"]

# Database
DATABASE_URL=postgresql://user:pass@production-host:5432/database

# API Keys
GROQ_API_KEY=production-key
AMADEUS_API_KEY=production-key
```

## 🔐 Security

### CORS Configuration

For production, configure specific domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Authentication

The system uses Supabase Auth for:
- User registration
- Login
- Session management
- JWT tokens

## 📈 Monitoring

### Health Checks

- `GET /health` - Server status
- `GET /pool-status` - Database status
- `GET /` - General information

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🆘 Support

If you have problems or questions:

1. Check the documentation in `/docs`
2. Check existing issues
3. Create a new issue with specific details
4. Use the `CORS_SOLUTION.md` file for CORS problems

## 🏆 Key Features

- ✅ **Complete REST API** with FastAPI
- ✅ **Real-time Chat** with WebSockets
- ✅ **Artificial Intelligence** with Groq LLaMA 3.1
- ✅ **Graph Database** with Neo4j
- ✅ **Amadeus Integration** for flights and hotels
- ✅ **Voting System** democratic
- ✅ **Smart Preferences** stored in Neo4j
- ✅ **Secure Authentication** with Supabase
- ✅ **Group Planning** collaborative
- ✅ **Interactive Documentation** with Swagger

---

<div align="center">
  <p>Made with ❤️ for travelers by travelers</p>
  <p>
    <a href="https://localhost:8000/docs">📚 API Documentation</a> •
    <a href="https://localhost:8000/health">🏥 Server Status</a> •
    <a href="https://github.com/your-username/travel-prosus/issues">🐛 Report Bug</a>
  </p>
</div>

---venv\Scripts\activate