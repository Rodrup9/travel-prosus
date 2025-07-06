# routers/preferences.py
from fastapi import APIRouter, Query
from models.preferences import UserPreferenceResponse
from typing import List, Optional
from servies.preference_service import PreferenceService

router = APIRouter()
preference_service = PreferenceService()

@router.get("/preferences/users", response_model=UserPreferenceResponse)
async def obtener_preferencias_usuarios(
  sql_ids: Optional[List[str]] = Query(None, description="ID O IDs de SQL a consultar")
):

    return await preference_service.get_preferences(sql_ids)
