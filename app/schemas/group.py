from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class GroupBase(BaseModel):
    name: str
    status: Optional[bool] = True


class GroupCreate(GroupBase):
    host_id: UUID


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None


class GroupOut(GroupBase):
    id: UUID
    host_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
