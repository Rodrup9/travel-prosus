# app/schemas/flight.py

from pydantic import BaseModel
from datetime import datetime
import uuid
from typing import Optional

class FlightBase(BaseModel):
    trip_id: uuid.UUID
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    status: Optional[bool] = True

class FlightCreate(FlightBase):
    pass

class FlightUpdate(BaseModel):
    airline: Optional[str] = None
    departure_airport: Optional[str] = None
    arrival_airport: Optional[str] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    price: Optional[float] = None
    status: Optional[bool] = None

class FlightResponse(FlightBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
