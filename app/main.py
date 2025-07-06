from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import users
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Aquí se ejecuta el evento startup
    await init_db()
    yield
    # Aquí se ejecutaría shutdown si lo necesitas

app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/users", tags=["Usuarios"])
