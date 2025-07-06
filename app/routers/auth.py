from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from app.schemas.auth import LoginRequest, RegisterRequest
from app.middleware.verify_session import get_verify_session
from app.supabaseClient import get_supabase_client
from app.database import get_db
from app.services.user import UserService
from sqlalchemy.orm import Session
supabase = get_supabase_client()
router = APIRouter()


@router.post("/auth/login")
def login_user(login_data: LoginRequest):
    try:       
        print("login_user")
        print(login_data.email, login_data.password)
        response = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password,
        })
        print(response)
        return {
            "user": response.user,
            "session": response.session
        }
        
    except Exception as e:
        print(f"Error en login_user: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")



@router.get("/auth/logout")
def logout_user():
    try:
        response = supabase.auth.sign_out()
        print(response)
        return {
            "message": "User logged out successfully",
        }
    except Exception as e:
        print(f"Error en logout_user: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    

@router.get("/auth/me")
async def get_current_user_info(current_user = Depends(get_verify_session),db: Session = Depends(get_db)):
    """Obtiene la información del usuario autenticado"""
    print("current_user",current_user.id)
    users = UserService.get_user_by_id(db,current_user.id)
    return {
        "user": users
    }

