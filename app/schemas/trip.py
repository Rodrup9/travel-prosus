# app/schemas/trip.py
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from app.schemas.itinerary import ItineraryCreateCascade
from app.schemas.flight import FlightCreateCascade
from app.schemas.hotel import HotelCreateCascade
import uuid

class TripBase(BaseModel):
    group_id: uuid.UUID
    destination: str
    start_date: Optional[date] = None  # ✅ Permitir NULL
    end_date: Optional[date] = None    # ✅ Permitir NULL
    status: Optional[bool] = True

class TripCreate(TripBase):
    itineraries: Optional[List[ItineraryCreateCascade]] = None
    flights: Optional[List[FlightCreateCascade]] = None
    hotels: Optional[List[HotelCreateCascade]] = None

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
