from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import users, groups, trips, itineraries, flights, hotels, votes, group_chat, group_members, ia_chat, auth, websocket_chat, agent_preferences
from app.database import init_db, engine
# from app.neo4j_client import Neo4jClient
from app.routers import preferences_neo4j

# neo4j_client = Neo4jClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispose()
    print("Pool de conexiones cerrado")

app = FastAPI(lifespan=lifespan)

# Configurar CORS con configuración más específica
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Middleware personalizado para agregar headers CORS adicionales
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Agregar headers CORS adicionales
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
    response.headers["Access-Control-Expose-Headers"] = "Content-Length, Content-Type"
    
    return response

# Manejar solicitudes OPTIONS para preflight
@app.options("/{full_path:path}")
async def options_handler(request: Request, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

# Incluir routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])
app.include_router(trips.router, prefix="/trips", tags=["Trips"])
app.include_router(itineraries.router, prefix="/itineraries", tags=["Itineraries"])
app.include_router(flights.router, prefix="/flights", tags=["Flights"])
app.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
app.include_router(votes.router, prefix="/votes", tags=["Votes"])
app.include_router(group_chat.router, prefix="/group_chat", tags=["Group Chat"])
app.include_router(group_members.router)
app.include_router(ia_chat.router, prefix="/ia_chat", tags=["IA Chat"])
app.include_router(preferences_neo4j.router)
app.include_router(auth.router)
app.include_router(websocket_chat.router, tags=["WebSocket Chat"])
app.include_router(agent_preferences.router)

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el servidor funciona"""
    return {
        "message": "Travel Prosus API está funcionando",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "service": "travel-prosus-api",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/cors-test")
async def cors_test():
    """Endpoint específico para probar CORS"""
    return {
        "message": "CORS está funcionando correctamente",
        "headers_sent": "Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers"
    }

@app.get("/pool-status")
async def pool_status():
    return {
        "status": "Pool de conexiones activo",
        "engine_type": str(type(engine))
    }