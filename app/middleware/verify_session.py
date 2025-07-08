from fastapi import HTTPException, Header
from typing import Optional
from app.supabaseClient import get_supabase_client
import asyncio
import time

async def get_verify_session(authorization: Optional[str] = Header(None)):
    """
    Verifica el token JWT y retorna los datos del usuario con timeout
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token de autorización requerido")
  
    try:  
        start_time = time.time()
        print(f"🔐 Verificando token...")
        
        token = authorization.replace("Bearer ", "")
        supabase = get_supabase_client()
        
        # Agregar timeout para la verificación del token
        loop = asyncio.get_event_loop()
        user_response = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: supabase.auth.get_user(token)),
            timeout=5.0
        )
        
        elapsed_time = time.time() - start_time
        print(f"✅ Token verificado en {elapsed_time:.2f}s")
        
        return user_response.user
        
    except asyncio.TimeoutError:
        print("⏰ Timeout verificando token")
        raise HTTPException(
            status_code=408, 
            detail="Timeout verifying authorization token"
        )
    except Exception as e:
        print(f"❌ Error verificando token: {e}")
        raise HTTPException(
            status_code=401, 
            detail="Token inválido"
        )