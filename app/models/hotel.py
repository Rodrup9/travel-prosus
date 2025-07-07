# app/models/hotel.py

from sqlalchemy import String, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from sqlalchemy.sql import func
import uuid


class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id"))
    name: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String)
    price_per_night: Mapped[float] = mapped_column(Numeric)
    rating: Mapped[float] = mapped_column(Numeric)
    link: Mapped[str] = mapped_column(String)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    trip = relationship("Trip", back_populates="hotels")