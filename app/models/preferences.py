from typing import List, Optional
from pydantic import BaseModel

class UserPreferenceBase(BaseModel):
    user_id: str
    Usuario: str
    sql_id: str
    Destinos: List[str]
    Actividades: List[str]
    Precios: List[str]
    Alojamientos: List[str]
    Transportes: List[str]
    Motivaciones: List[str]

class UserPreferenceResponse(BaseModel):
    status: str = "success"
    message: str = "Preferences retrieved successfully"
    data: List[UserPreferenceBase]
    user_count: int