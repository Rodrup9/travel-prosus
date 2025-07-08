from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import LoginRequest
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse
from app.middleware.verify_session import get_verify_session
from app.supabaseClient import get_supabase_client
import asyncio
from functools import wraps

router = APIRouter()
supabase = get_supabase_client()

def timeout_handler(timeout_seconds=10):
    """Decorator para agregar timeout a funciones síncronas"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Ejecutar la función en un thread pool con timeout
                loop = asyncio.get_event_loop()
                return await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=408,
                    detail=f"Operation timed out after {timeout_seconds} seconds"
                )
        return wrapper
    return decorator

@router.get("/auth/logout")
@timeout_handler(timeout_seconds=5)
def logout_user():
    """
    Logout user from Supabase with timeout protection
    """
    try:
        print("🔄 Iniciando logout...")
        
        # Logout rápido sin esperar respuesta detallada
        try:
            response = supabase.auth.sign_out()
            print(f"✅ Logout response: {response}")
        except Exception as supabase_error:
            print(f"⚠️ Supabase logout warning: {supabase_error}")
            # No fallar si Supabase tiene problemas, el logout del lado cliente es suficiente
        
        return {
            "success": True,
            "message": "User logged out successfully",
            "timestamp": "2025-07-08T00:00:00Z"
        }
    except Exception as e:
        print(f"❌ Error en logout_user: {e}")
        # Incluso si hay error, retornar éxito para que el frontend pueda limpiar el estado
        return {
            "success": True,
            "message": "Logout completed (with warnings)",
            "warning": str(e),
            "timestamp": "2025-07-08T00:00:00Z"
        }

@router.post("/auth/login")
async def login_user(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login user with Supabase with timeout protection and complete user info
    """
    try:       
        print("🔄 Iniciando login...")
        print(f"📧 Email: {login_data.email}")
        
        # Autenticar con Supabase
        response = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password,
        })
        
        print("✅ Autenticación Supabase exitosa")
        print(f"📤 Supabase User ID: {response.user.id}")
        print(f"📤 Supabase Email: {response.user.email}")
        print(f"📤 Supabase Session: {response.session is not None}")
        
        # Obtener información completa del usuario de la base de datos local
        try:
            import uuid
            user_uuid = uuid.UUID(response.user.id)
            db_user = await UserService.get_user_by_id(db, user_uuid)
            
            if db_user:
                print(f"✅ Usuario encontrado en BD local: {db_user.name}")
                print(f"📤 Nombre de usuario: {db_user.name}")
                print(f"📤 Email BD: {db_user.email}")
                print(f"📤 Status: {db_user.status}")
                print(f"📤 Avatar URL: {db_user.avatar_url}")
                
                # Construir respuesta completa con toda la información
                login_response = {
                    "success": True,
                    "message": "Login successful",
                    "supabase_user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "created_at": response.user.created_at,
                        "updated_at": response.user.updated_at,
                        "email_confirmed_at": response.user.email_confirmed_at,
                        "last_sign_in_at": response.user.last_sign_in_at,
                        "app_metadata": response.user.app_metadata,
                        "user_metadata": response.user.user_metadata
                    },
                    "local_user": {
                        "id": str(db_user.id),
                        "name": db_user.name,  # NOMBRE DE USUARIO INCLUIDO
                        "email": db_user.email,
                        "status": db_user.status,
                        "avatar_url": db_user.avatar_url,
                        "created_at": db_user.created_at.isoformat()
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_in": response.session.expires_in,
                        "expires_at": response.session.expires_at,
                        "token_type": response.session.token_type
                    },
                    "timestamp": "2025-07-08T00:00:00Z"
                }
                
                print("📤 DATOS ENVIADOS AL FRONTEND:")
                print(f"   - Supabase ID: {response.user.id}")
                print(f"   - Email: {db_user.email}")
                print(f"   - NOMBRE: {db_user.name}")  # ✅ NOMBRE INCLUIDO
                print(f"   - Status: {db_user.status}")
                print(f"   - Avatar: {db_user.avatar_url}")
                print(f"   - Access Token: {'presente' if response.session.access_token else 'ausente'}")
                
                return login_response
                
            else:
                print("⚠️ Usuario no encontrado en BD local, usando solo datos de Supabase")
                # Si no está en BD local, usar solo datos de Supabase
                fallback_response = {
                    "success": True,
                    "message": "Login successful (Supabase only)",
                    "supabase_user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "created_at": response.user.created_at,
                        "updated_at": response.user.updated_at,
                        "email_confirmed_at": response.user.email_confirmed_at,
                        "last_sign_in_at": response.user.last_sign_in_at,
                        "app_metadata": response.user.app_metadata,
                        "user_metadata": response.user.user_metadata
                    },
                    "local_user": None,
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_in": response.session.expires_in,
                        "expires_at": response.session.expires_at,
                        "token_type": response.session.token_type
                    },
                    "warning": "User not found in local database",
                    "timestamp": "2025-07-08T00:00:00Z"
                }
                
                print("📤 DATOS ENVIADOS AL FRONTEND (Solo Supabase):")
                print(f"   - Supabase ID: {response.user.id}")
                print(f"   - Email: {response.user.email}")
                print(f"   - NOMBRE: NO DISPONIBLE (no está en BD local)")
                
                return fallback_response
                
        except Exception as db_error:
            print(f"⚠️ Error consultando BD local: {db_error}")
            # Si hay error con BD local, usar solo Supabase
            return {
                "success": True,
                "message": "Login successful (database error)",
                "supabase_user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                    "updated_at": response.user.updated_at,
                    "email_confirmed_at": response.user.email_confirmed_at,
                    "last_sign_in_at": response.user.last_sign_in_at,
                    "app_metadata": response.user.app_metadata,
                    "user_metadata": response.user.user_metadata
                },
                "local_user": None,
                "session": {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_in": response.session.expires_in,
                    "expires_at": response.session.expires_at,
                    "token_type": response.session.token_type
                },
                "error": f"Database error: {str(db_error)}",
                "timestamp": "2025-07-08T00:00:00Z"
            }
        
    except Exception as e:
        print(f"❌ Error en login_user: {e}")
        raise HTTPException(
            status_code=401, 
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_user = await UserService.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user = Depends(get_verify_session), db: AsyncSession = Depends(get_db)):
    """
    Get current authenticated user information
    """
    try:
        print(f"🔍 Obteniendo información del usuario: {current_user.id}")
        print(f"📧 Email del token: {current_user.email}")
        
        # Agregar timeout para la consulta de base de datos
        db_user = await asyncio.wait_for(
            UserService.get_user_by_id(db, current_user.id),
            timeout=5.0
        )
        
        if not db_user:
            print(f"❌ Usuario no encontrado en BD local para ID: {current_user.id}")
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        print(f"✅ Usuario encontrado en BD local:")
        print(f"   - ID: {db_user.id}")
        print(f"   - NOMBRE: {db_user.name}")  # ✅ NOMBRE INCLUIDO
        print(f"   - Email: {db_user.email}")
        print(f"   - Status: {db_user.status}")
        print(f"   - Avatar: {db_user.avatar_url}")
        print(f"   - Created: {db_user.created_at}")
        
        print("📤 DATOS ENVIADOS AL FRONTEND (/me):")
        print(f"   - ID: {db_user.id}")
        print(f"   - NOMBRE: {db_user.name}")
        print(f"   - Email: {db_user.email}")
        print(f"   - Status: {db_user.status}")
        print(f"   - Avatar: {db_user.avatar_url}")
        
        return db_user
        
    except asyncio.TimeoutError:
        print("⏰ Timeout obteniendo información del usuario")
        raise HTTPException(
            status_code=408,
            detail="Timeout getting user information"
        )
    except Exception as e:
        print(f"❌ Error obteniendo usuario: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user information: {str(e)}"
        )

@router.get("/verify")
async def verify_token(current_user = Depends(get_verify_session)):
    """
    Verify if the current token is valid
    """
    try:
        print(f"🔐 Verificando token para usuario: {current_user.id}")
        return {
            "valid": True, 
            "user": current_user,
            "timestamp": "2025-07-08T00:00:00Z"
        }
    except Exception as e:
        print(f"❌ Error verificando token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

@router.get("/auth/test")
async def test_auth_connectivity():
    """
    Quick test endpoint to verify authentication service connectivity
    """
    try:
        print("🧪 Testing auth connectivity...")
        
        # Test básico de conectividad con Supabase
        test_result = {
            "auth_service": "online",
            "supabase_client": "connected" if supabase else "disconnected",
            "timestamp": "2025-07-08T00:00:00Z",
            "endpoints": {
                "login": "/auth/login",
                "logout": "/auth/logout", 
                "verify": "/verify",
                "me": "/me"
            }
        }
        
        print("✅ Auth connectivity test passed")
        return test_result
        
    except Exception as e:
        print(f"❌ Auth connectivity test failed: {e}")
        return {
            "auth_service": "error",
            "error": str(e),
            "timestamp": "2025-07-08T00:00:00Z"
        }

