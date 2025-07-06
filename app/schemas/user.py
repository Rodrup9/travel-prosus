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
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[bool] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True