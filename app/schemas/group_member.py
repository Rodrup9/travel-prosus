from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class GroupMemberBase(BaseModel):
    group_id: uuid.UUID
    user_id: uuid.UUID
    status: Optional[bool] = True

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMemberUpdate(BaseModel):
    status: Optional[bool] = None

class GroupMemberResponse(GroupMemberBase):
    group_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True