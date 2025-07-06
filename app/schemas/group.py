from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[bool] = True


class GroupCreate(GroupBase):
    creator_id: UUID


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None


class GroupOut(GroupBase):
    id: UUID
    creator_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
