# app/models/trip.py
from sqlalchemy import String, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models.group import Group
if TYPE_CHECKING:
    from app.models.flight import Flight

class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    group = relationship("Group", back_populates="trips")
    flights = relationship("Flight", back_populates="trip")
    itineraries = relationship("Itinerary", back_populates="trip")
    hotels = relationship("Hotel", back_populates="trip")
