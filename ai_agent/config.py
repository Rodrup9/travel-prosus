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
    TEMPERATURE: float = 0.3  # Reducido para respuestas más consistentes
    MAX_TOKENS: int = 8192  # Aumentado para respuestas más detalladas
    TOOLS_ENABLED: bool = True  # Habilitar el uso de herramientas
    JSON_MODE: bool = True  # Habilitar modo JSON para respuestas estructuradas
    
    # Configuración específica para el agente de viajes
    ITINERARY_TEMPERATURE: float = 0.2  # Temperatura más baja para itinerarios
    ITINERARY_MAX_TOKENS: int = 12000  # Más tokens para itinerarios detallados
    
    # Configuración para búsquedas
    SEARCH_TEMPERATURE: float = 0.1  # Temperatura muy baja para búsquedas precisas
    SEARCH_MAX_TOKENS: int = 4096
    
    # Amadeus API credentials
    AMADEUS_API_KEY: str = env_values.get('AMADEUS_API_KEY') or ''
    AMADEUS_API_SECRET: str = env_values.get('AMADEUS_API_SECRET') or ''
    
    # Weather API credentials (opcional, usamos web_search por ahora)
    WEATHER_API_KEY: Optional[str] = None
    
    # Web search settings
    WEB_SEARCH_ENABLED: bool = True  # Habilitar búsqueda web
    
    # Configuración de contexto
    MAX_CHAT_HISTORY: int = 20  # Número máximo de mensajes a considerar
    MAX_USER_CONTEXT: int = 5   # Número máximo de interacciones por usuario
    
    # ID especial para identificar los mensajes del agente en el chat
    AGENT_USER_ID: uuid.UUID = uuid.UUID('00000000-0000-0000-0000-000000000000')
    
    # Configuración de herramientas
    ENABLE_FLIGHT_SEARCH: bool = True
    ENABLE_HOTEL_SEARCH: bool = True
    ENABLE_WEATHER_SEARCH: bool = True
    ENABLE_WEB_SEARCH: bool = True
    
    # Configuración de búsquedas
    MAX_FLIGHT_RESULTS: int = 5
    MAX_HOTEL_RESULTS: int = 5
    SEARCH_RADIUS_KM: int = 50

# Debug: Imprimir los valores cargados
print("=== Debug: Valores cargados del .env ===")
print(f"GROQ_API_KEY: {env_values.get('GROQ_API_KEY')}")
print("================================")

settings = GroqSettings() 