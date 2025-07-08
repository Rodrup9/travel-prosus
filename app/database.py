# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import create_engine
from typing import Generator, AsyncGenerator
import os

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/travel_prosus")

# Asegurarse de que la URL use el prefijo postgresql+asyncpg://
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

# Motor asíncrono
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Motor síncrono para operaciones que requieren sincronización
sync_engine = create_engine("postgresql://postgres:postgres@localhost:5432/travel_prosus")
SyncSessionLocal = sessionmaker(
    bind=sync_engine, 
    class_=Session, 
    expire_on_commit=False
)

# Base para los modelos
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db() -> Generator[Session, None, None]:
    """Función para obtener sesiones síncronas cuando sea necesario"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Inicializa la conexión a la base de datos"""
    print("Conexión a la base de datos establecida - Pool de conexiones asíncrono creado")