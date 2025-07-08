# app/schemas/itinerary.py

from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional
import uuid


class ItineraryBase(BaseModel):
    trip_id: uuid.UUID
    day: date
    activity: str
    location: str
    start_time: time
    end_time: time
    status: Optional[bool] = True


class ItineraryCreate(ItineraryBase):
    pass

class ItineraryCreateCascade(BaseModel):
    day: date
    activity: str
    location: str
    start_time: time
    end_time: time
    status: Optional[bool] = True


class ItineraryUpdate(BaseModel):
    day: Optional[date] = None
    activity: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[bool] = None


class ItineraryResponse(ItineraryBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
