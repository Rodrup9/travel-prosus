# app/schemas/vote.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class VoteBase(BaseModel):
    trip_id: uuid.UUID
    user_id: uuid.UUID
    vote: bool
    comment: Optional[str] = None
    status: Optional[bool] = True

class VoteCreate(VoteBase):
    pass

class VoteUpdate(BaseModel):
    vote: Optional[bool] = None
    comment: Optional[str] = None
    status: Optional[bool] = None

class VoteResponse(VoteBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
