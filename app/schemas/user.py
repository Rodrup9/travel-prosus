from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    avatar_url: Optional[str] = None
    status: Optional[bool] = True

class UserRead(BaseModel):
    id: UUID
    name: str
    email: str
    avatar_url: Optional[str]
    created_at: datetime
    status: bool

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    status: Optional[bool] = None
