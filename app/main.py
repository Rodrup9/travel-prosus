from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import users
from app.database import init_db
from app.neo4j_client import Neo4jClient
from app.routers import preferences_neo4j
neo4j_client = Neo4jClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Aquí se ejecuta el evento startup
    await init_db()
    yield
    # Aquí se ejecutaría shutdown si lo necesitas

app = FastAPI(lifespan=lifespan)

#app.include_router(preferences_neo4j.router)
app.include_router(users.router, prefix="/users", tags=["Usuarios"])
app.include_router(preferences_neo4j.router)
