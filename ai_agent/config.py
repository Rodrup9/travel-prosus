from typing import Optional
from pydantic_settings import BaseSettings

class GroqSettings(BaseSettings):
    GROQ_API_KEY: str
    MODEL_NAME: str = "llama-3.1-8b-instant"
    MAX_TOKENS: int = 4096  # Ajustado para respuestas más concisas
    TEMPERATURE: float = 0.7
    TOOLS_ENABLED: bool = True  # Habilitar el uso de herramientas
    JSON_MODE: bool = True  # Habilitar modo JSON para respuestas estructuradas
    
    # Amadeus API credentials
    AMADEUS_API_KEY: str
    AMADEUS_API_SECRET: str
    
    class Config:
        env_file = ".env"

settings = GroqSettings() 