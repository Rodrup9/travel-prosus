from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime
    email_confirmed_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None
    role: str
    aud: str
    app_metadata: dict
    user_metadata: dict

class LoginResponse(BaseModel):
    user: UserResponse
    session: dict

class RegisterResponse(BaseModel):
    message: str
    user: UserResponse