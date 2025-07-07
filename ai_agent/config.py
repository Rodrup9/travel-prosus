from typing import Optional
from pydantic_settings import BaseSettings
import uuid
import os
from dotenv import load_dotenv, dotenv_values

# Cargar valores directamente del archivo .env
env_values = dotenv_values(".env")

class GroqSettings(BaseSettings):
    model_config = {
        "extra": "allow",
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    # Usar valores del archivo .env directamente
    GROQ_API_KEY: str = env_values.get('GROQ_API_KEY') or ''
    MODEL_NAME: str = "llama-3.1-8b-instant"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096  # Ajustado para respuestas más concisas
    TOOLS_ENABLED: bool = True  # Habilitar el uso de herramientas
    JSON_MODE: bool = True  # Habilitar modo JSON para respuestas estructuradas
    
    # Amadeus API credentials
    AMADEUS_API_KEY: str = env_values.get('AMADEUS_API_KEY') or ''
    AMADEUS_API_SECRET: str = env_values.get('AMADEUS_API_SECRET') or ''
    
    # Weather API credentials (opcional, usamos web_search por ahora)
    WEATHER_API_KEY: Optional[str] = None
    
    # Web search settings
    WEB_SEARCH_ENABLED: bool = True  # Habilitar búsqueda web
    
    # ID especial para identificar los mensajes del agente en el chat
    AGENT_USER_ID: uuid.UUID = uuid.UUID('00000000-0000-0000-0000-000000000000')

# Debug: Imprimir los valores cargados
print("=== Debug: Valores cargados del .env ===")
print(f"GROQ_API_KEY: {env_values.get('GROQ_API_KEY')}")
print("================================")

settings = GroqSettings() 