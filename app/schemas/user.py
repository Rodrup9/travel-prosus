from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class UserBase(BaseModel):
    name: str
    email: str
    status: Optional[bool] = True
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[bool] = None
    avatar_url: Optional[str] = None

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    status: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True