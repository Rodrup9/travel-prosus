from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class GroqSettings(BaseSettings):
    GROQ_API_KEY: str
    MODEL_NAME: str = "mixtral-8x7b-32768"
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    TOOLS_ENABLED: bool = True
    JSON_MODE: bool = True
    
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"  # Permite campos adicionales en el .env
    )

settings = GroqSettings() 