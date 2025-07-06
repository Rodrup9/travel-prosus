# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# URL de la base de datos
# SUPABASE_URL = os.getenv("SUPABASE_URL");
DATABASE_URL = os.getenv("DATABASE_URL");

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Número base de conexiones en el pool
    max_overflow=30,       # Conexiones adicionales cuando el pool está lleno
    pool_pre_ping=True,    # Verifica conexiones antes de usarlas
    pool_recycle=3600,     # Recicla conexiones después de 1 hora
    echo=False             # True para debug SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Inicializa la conexión a la base de datos"""
    print("Conexión a la base de datos establecida - Pool de conexiones creado")