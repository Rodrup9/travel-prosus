from typing import Optional
from pydantic_settings import BaseSettings
import uuid

class GroqSettings(BaseSettings):
    GROQ_API_KEY: str
    MODEL_NAME: str = "llama-3.1-8b-instant"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4096  # Ajustado para respuestas más concisas
    TOOLS_ENABLED: bool = True  # Habilitar el uso de herramientas
    JSON_MODE: bool = True  # Habilitar modo JSON para respuestas estructuradas
    
    # Amadeus API credentials
    AMADEUS_API_KEY: str
    AMADEUS_API_SECRET: str
    
    # Weather API credentials (opcional, usamos web_search por ahora)
    WEATHER_API_KEY: Optional[str] = None
    
    # Web search settings
    WEB_SEARCH_ENABLED: bool = True  # Habilitar búsqueda web
    
    # ID especial para identificar los mensajes del agente en el chat
    AGENT_USER_ID: uuid.UUID = uuid.UUID('00000000-0000-0000-0000-000000000000')

    class Config:
        env_file = ".env"

settings = GroqSettings() 