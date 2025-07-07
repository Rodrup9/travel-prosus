from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class IAChatBase(BaseModel):
    user_id: uuid.UUID
    group_id: uuid.UUID
    message: str
    status: Optional[bool] = True

class IAChatCreate(IAChatBase):
    pass

class IAChatUpdate(BaseModel):
    message: Optional[str] = None
    status: Optional[bool] = None

class IAChatResponse(IAChatBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
