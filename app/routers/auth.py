from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import LoginRequest
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse
from app.middleware.verify_session import get_verify_session
from app.supabaseClient import get_supabase_client

router = APIRouter()
supabase = get_supabase_client()

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

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_user = await UserService.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user = Depends(get_verify_session), db: AsyncSession = Depends(get_db)):
    db_user = await UserService.get_user_by_id(db, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@router.get("/verify")
async def verify_token(current_user = Depends(get_verify_session)):
    return {"valid": True, "user": current_user}

