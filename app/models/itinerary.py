# app/models/itinerary.py

from sqlalchemy import String, Date, Time, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import time, date
from app.database import Base
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.trip import Trip

class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    day: Mapped[date]
    activity: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    start_time: Mapped[time]
    end_time: Mapped[time]
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    trip = relationship("Trip", back_populates="itineraries")
