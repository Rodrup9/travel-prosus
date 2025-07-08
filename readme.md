# 🌍 Travel Prosus - Plataforma de Planificación de Viajes con IA

<div align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j">
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/WebSocket-010101?style=for-the-badge&logo=websocket&logoColor=white" alt="WebSocket">
  <img src="https://img.shields.io/badge/Groq-FF6B35?style=for-the-badge&logo=groq&logoColor=white" alt="Groq">
</div>

## 📖 Descripción

Travel Prosus es una plataforma avanzada de planificación de viajes que utiliza inteligencia artificial para crear experiencias de viaje personalizadas. La aplicación combina tecnologías modernas como FastAPI, Neo4j, Supabase y WebSockets para ofrecer una experiencia completa de planificación grupal de viajes.

### 🚀 Características Principales

- **🤖 Agente de IA Inteligente**: Utiliza Groq LLaMA 3.1 para recomendaciones personalizadas
- **👥 Planificación Grupal**: Colaboración en tiempo real entre miembros del grupo
- **💬 Chat en Tiempo Real**: Comunicación instantánea con WebSockets
- **✈️ Integración con Amadeus**: Búsqueda de vuelos y hoteles en tiempo real
- **📊 Sistema de Preferencias**: Almacenamiento inteligente en Neo4j
- **🗳️ Sistema de Votación**: Decisiones democráticas para el grupo
- **📱 API REST Completa**: Endpoints para todas las funcionalidades
- **🔐 Autenticación Segura**: Sistema de autenticación con Supabase

## 🏗️ Arquitectura del Sistema

```
Travel Prosus
├── 🧠 AI Agent (Groq LLaMA 3.1)
│   ├── Recomendaciones personalizadas
│   ├── Búsqueda de vuelos/hoteles
│   └── Análisis de preferencias
├── 🏛️ Backend (FastAPI)
│   ├── API REST
│   ├── WebSocket Chat
│   ├── Autenticación
│   └── Gestión de datos
├── 📊 Bases de Datos
│   ├── PostgreSQL (Supabase) - Datos principales
│   └── Neo4j - Preferencias y relaciones
└── 🌐 Servicios Externos
    ├── Amadeus API - Vuelos y hoteles
    ├── Supabase - Base de datos y auth
    └── Groq - Inteligencia artificial
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLModel**: ORM asíncrono para PostgreSQL
- **Supabase**: Base de datos PostgreSQL como servicio
- **Neo4j**: Base de datos de grafos para preferencias
- **WebSockets**: Comunicación en tiempo real
- **Uvicorn**: Servidor ASGI

### IA y Servicios
- **Groq**: API de IA con LLaMA 3.1
- **Amadeus API**: Búsqueda de vuelos y hoteles
- **Neo4j Aura**: Base de datos de grafos en la nube

### Herramientas de Desarrollo
- **Python 3.12+**: Lenguaje principal
- **Pydantic**: Validación de datos
- **python-dotenv**: Gestión de variables de entorno
- **AsyncPG**: Driver asíncrono para PostgreSQL

## 📋 Requisitos Previos

- Python 3.12 o superior
- Node.js 18+ (para el frontend)
- Cuenta en Supabase
- Cuenta en Neo4j Aura
- API Key de Amadeus
- API Key de Groq

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/travel-prosus.git
cd travel-prosus
```

### 2. Configurar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

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

### 5. Configurar Bases de Datos

#### PostgreSQL (Supabase)
1. Crea un proyecto en [Supabase](https://supabase.com)
2. Obtén la URL y la clave anónima
3. Las tablas se crearán automáticamente al iniciar la aplicación

#### Neo4j
1. Crea una instancia en [Neo4j Aura](https://neo4j.com/aura/)
2. Obtén las credenciales de conexión
3. La base de datos se configurará automáticamente

### 6. Iniciar el Servidor

```bash
# Opción 1: Usar el script de PowerShell (Windows)
.\start_server.ps1

# Opción 2: Usar uvicorn directamente
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opción 3: Usar el script de Python
python start_server.py
```

El servidor estará disponible en `http://localhost:8000`

## 📚 Documentación de API

### Endpoints Principales

#### 🔐 Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/register` - Registrar usuario
- `POST /auth/logout` - Cerrar sesión

#### 👥 Usuarios
- `GET /users` - Obtener todos los usuarios
- `GET /users/{user_id}` - Obtener usuario específico
- `POST /users` - Crear nuevo usuario
- `PUT /users/{user_id}` - Actualizar usuario
- `DELETE /users/{user_id}` - Eliminar usuario

#### 🏠 Grupos
- `GET /groups` - Obtener todos los grupos
- `GET /groups/{group_id}` - Obtener grupo específico
- `POST /groups` - Crear nuevo grupo
- `PUT /groups/{group_id}` - Actualizar grupo
- `DELETE /groups/{group_id}` - Eliminar grupo

#### ✈️ Vuelos
- `GET /flights` - Obtener vuelos
- `GET /flights/{flight_id}` - Obtener vuelo específico
- `POST /flights` - Crear vuelo
- `PUT /flights/{flight_id}` - Actualizar vuelo
- `DELETE /flights/{flight_id}` - Eliminar vuelo

#### 🏨 Hoteles
- `GET /hotels` - Obtener hoteles
- `GET /hotels/{hotel_id}` - Obtener hotel específico
- `POST /hotels` - Crear hotel
- `PUT /hotels/{hotel_id}` - Actualizar hotel
- `DELETE /hotels/{hotel_id}` - Eliminar hotel

#### 🗳️ Votaciones
- `GET /votes` - Obtener votaciones
- `POST /votes` - Crear votación
- `GET /votes/{vote_id}` - Obtener votación específica

#### 📊 Preferencias
- `GET /preferences/user/{user_id}` - Obtener preferencias de usuario
- `GET /preferences/users?group_id={group_id}` - Obtener preferencias del grupo

### 🔍 Documentación Interactiva

Una vez que el servidor esté en funcionamiento, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤖 Agente de IA

### Funcionalidades del Agente

El agente de IA utiliza **Groq LLaMA 3.1** para proporcionar:

1. **Recomendaciones de Destinos**: Basadas en preferencias del usuario
2. **Búsqueda de Vuelos**: Integración con Amadeus API
3. **Búsqueda de Hoteles**: Recomendaciones personalizadas
4. **Análisis de Preferencias**: Usando Neo4j para almacenar patrones
5. **Itinerarios Personalizados**: Creación automática de planes de viaje

### Herramientas del Agente

```python
# Ejemplo de uso del agente
from ai_agent.agent_service import AgentService

agent = AgentService()

# Búsqueda de vuelos
flights = await agent.search_flights(
    origin="MAD",
    destination="BCN",
    departure_date="2024-12-01",
    return_date="2024-12-05"
)

# Recomendaciones de hoteles
hotels = await agent.search_hotels(
    destination="Barcelona",
    check_in="2024-12-01",
    check_out="2024-12-05"
)
```

## 💬 Chat en Tiempo Real

### Características del Chat

- **WebSocket**: Comunicación bidireccional instantánea
- **Persistencia**: Mensajes guardados en Supabase
- **Indicadores de Escritura**: Muestra cuando alguien está escribiendo
- **Reconexión Automática**: Manejo de desconexiones
- **Múltiples Canales**: Chat por grupo de viaje

### Conexión WebSocket

```javascript
// Ejemplo de conexión desde el frontend
const ws = new WebSocket('ws://localhost:8000/ws/chat/{group_id}');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Mensaje recibido:', data);
};

ws.send(JSON.stringify({
    type: 'message',
    content: 'Hola grupo!',
    user_id: 'user-uuid'
}));
```

### Tipos de Mensajes

- **message**: Mensaje de texto normal
- **typing**: Indicador de que el usuario está escribiendo
- **system**: Mensajes del sistema
- **ai_response**: Respuestas del agente de IA

## 🧪 Testing

### Verificar CORS

Abre `cors_test.html` en tu navegador para probar la comunicación con el backend.

### Ejecutar Tests

```bash
# Ejecutar tests de importación
python test_server.py

# Probar endpoints específicos
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/cors-test"
```

## 📊 Estructura de Datos

### Modelos Principales

```python
# Usuario
class User:
    id: UUID
    username: str
    email: str
    name: str
    created_at: datetime

# Grupo
class Group:
    id: UUID
    name: str
    description: str
    created_by: UUID
    created_at: datetime

# Viaje
class Trip:
    id: UUID
    group_id: UUID
    destination: str
    start_date: date
    end_date: date
    budget: float
```

## 🔧 Configuración Avanzada

### Personalizar el Agente de IA

```python
# En ai_agent/config.py
class GroqSettings:
    MODEL_NAME: str = "llama-3.1-8b-instant"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096
    TOOLS_ENABLED: bool = True
```

### Configurar Neo4j

```python
# Ejemplo de consulta de preferencias
MATCH (u:User)-[:PREFERS]->(p:Preference)
WHERE u.id_sql = $user_id
RETURN p.category, p.value, p.weight
```

## 🚀 Despliegue

### Usando Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variables de Entorno para Producción

```env
# CORS Configuration
CORS_ORIGINS=["https://tu-dominio.com", "https://www.tu-dominio.com"]

# Database
DATABASE_URL=postgresql://user:pass@production-host:5432/database

# API Keys
GROQ_API_KEY=production-key
AMADEUS_API_KEY=production-key
```

## 🔐 Seguridad

### Configuración CORS

Para producción, configura dominios específicos:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Autenticación

El sistema utiliza Supabase Auth para:
- Registro de usuarios
- Inicio de sesión
- Gestión de sesiones
- Tokens JWT

## 📈 Monitoreo

### Health Checks

- `GET /health` - Estado del servidor
- `GET /pool-status` - Estado de la base de datos
- `GET /` - Información general

### Logs

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación en `/docs`
2. Consulta los issues existentes
3. Crea un nuevo issue con detalles específicos
4. Usa el archivo `CORS_SOLUTION.md` para problemas de CORS

## 🏆 Características Destacadas

- ✅ **API REST Completa** con FastAPI
- ✅ **Chat en Tiempo Real** con WebSockets
- ✅ **Inteligencia Artificial** con Groq LLaMA 3.1
- ✅ **Base de Datos de Grafos** con Neo4j
- ✅ **Integración con Amadeus** para vuelos y hoteles
- ✅ **Sistema de Votación** democrático
- ✅ **Preferencias Inteligentes** almacenadas en Neo4j
- ✅ **Autenticación Segura** con Supabase
- ✅ **Planificación Grupal** colaborativa
- ✅ **Documentación Interactiva** con Swagger

---

<div align="center">
  <p>Hecho con ❤️ para viajeros por viajeros</p>
  <p>
    <a href="https://localhost:8000/docs">📚 Documentación API</a> •
    <a href="https://localhost:8000/health">🏥 Estado del Servidor</a> •
    <a href="https://github.com/tu-usuario/travel-prosus/issues">🐛 Reportar Bug</a>
  </p>
</div>

---venv\Scripts\activate