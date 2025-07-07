# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Asegurarse de que la URL use el prefijo postgresql+asyncpg://
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

# Motor asíncrono
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Motor síncrono para operaciones que requieren sincronización
sync_engine = create_engine("postgresql://postgres:postgres@localhost:5432/travel_prosus")

# Base para los modelos
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Inicializa la conexión a la base de datos"""
    print("Conexión a la base de datos establecida - Pool de conexiones asíncrono creado")