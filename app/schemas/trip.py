# app/schemas/trip.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
import uuid

class TripBase(BaseModel):
    group_id: uuid.UUID
    destination: str
    start_date: date
    end_date: date
    status: Optional[bool] = True

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[bool] = None

class TripResponse(TripBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
