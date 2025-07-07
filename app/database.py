# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Asegurarse de que la URL use el prefijo postgresql+asyncpg://
if DATABASE_URL and DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

# Crear el motor asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # True para debug SQL
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30
)

# Configurar la sesión asíncrona
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Inicializa la conexión a la base de datos"""
    print("Conexión a la base de datos establecida - Pool de conexiones asíncrono creado")