# app/schemas/hotel.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid


class HotelBase(BaseModel):
    trip_id: uuid.UUID
    name: str
    location: str
    price_per_night: float
    rating: float
    link: str
    status: Optional[bool] = True


class HotelCreate(HotelBase):
    pass


class HotelUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    price_per_night: Optional[float] = None
    rating: Optional[float] = None
    link: Optional[str] = None
    status: Optional[bool] = None


class HotelResponse(HotelBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
