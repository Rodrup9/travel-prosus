# app/models/flight.py

from sqlalchemy import String, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime

class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"))
    airline: Mapped[str] = mapped_column(String, nullable=False)
    departure_airport: Mapped[str] = mapped_column(String, nullable=False)
    arrival_airport: Mapped[str] = mapped_column(String, nullable=False)
    
    departure_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    # relationship
    trip = relationship("Trip", back_populates="flights")
