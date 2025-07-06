from fastapi import HTTPException, Header
from typing import Optional
from app.supabaseClient import get_supabase_client

def get_verify_session(authorization: Optional[str] = Header(None)):
    """Verifica el token JWT y retorna los datos del usuario"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token de autorización requerido")
  
    try:  
        token = authorization.replace("Bearer ", "")
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")