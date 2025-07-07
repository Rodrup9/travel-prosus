from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class GroupChatBase(BaseModel):
    user_id: uuid.UUID
    group_id: uuid.UUID
    message: str
    status: Optional[bool] = True

class GroupChatCreate(GroupChatBase):
    pass

class GroupChatUpdate(BaseModel):
    message: Optional[str] = None
    status: Optional[bool] = None

class GroupChatResponse(GroupChatBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
