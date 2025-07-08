# app/services/flight_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.flight import Flight
from app.schemas.flight import FlightCreate, FlightUpdate, FlightCreateCascade
from typing import Optional, List
import uuid


class FlightService:

    @staticmethod
    async def create_flight(db: AsyncSession, flight: FlightCreate) -> Flight:
        db_flight = Flight(
            id=uuid.uuid4(),
            trip_id=flight.trip_id,
            airline=flight.airline,
            departure_airport=flight.departure_airport,
            arrival_airport=flight.arrival_airport,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            price=flight.price,
            status=flight.status
        )
        try:
            db.add(db_flight)
            await db.commit()
            await db.refresh(db_flight)
            return db_flight
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear el vuelo: {str(e.orig)}")
        
    @staticmethod
    async def create_flight_cascade(db: AsyncSession, flight: FlightCreateCascade, trip_id: uuid.UUID) -> Flight:
        db_flight = Flight(
            id=uuid.uuid4(),
            trip_id=trip_id,
            airline=flight.airline,
            departure_airport=flight.departure_airport,
            arrival_airport=flight.arrival_airport,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            price=flight.price,
            status=flight.status
        )
        try:
            db.add(db_flight)
            await db.commit()
            await db.refresh(db_flight)
            return db_flight
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear el vuelo: {str(e.orig)}")

    @staticmethod
    async def get_flight_by_id(db: AsyncSession, flight_id: uuid.UUID) -> Optional[Flight]:
        result = await db.execute(select(Flight).filter(Flight.id == flight_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_flights(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Flight]:
        result = await db.execute(select(Flight).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_flights_by_trip(db: AsyncSession, trip_id: uuid.UUID) -> List[Flight]:
        result = await db.execute(select(Flight).filter(Flight.trip_id == trip_id))
        return result.scalars().all()

    @staticmethod
    async def update_flight(db: AsyncSession, flight_id: uuid.UUID, update_data: FlightUpdate) -> Optional[Flight]:
        result = await db.execute(select(Flight).filter(Flight.id == flight_id))
        db_flight = result.scalar_one_or_none()
        if not db_flight:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_flight, field, value)

        try:
            await db.commit()
            await db.refresh(db_flight)
            return db_flight
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al actualizar el vuelo: {str(e.orig)}")

    @staticmethod
    async def delete_flight(db: AsyncSession, flight_id: uuid.UUID) -> bool:
        result = await db.execute(select(Flight).filter(Flight.id == flight_id))
        db_flight = result.scalar_one_or_none()
        if not db_flight:
            return False

        await db.delete(db_flight)
        await db.commit()
        return True

    @staticmethod
    async def toggle_status(db: AsyncSession, flight_id: uuid.UUID) -> Optional[Flight]:
        result = await db.execute(select(Flight).filter(Flight.id == flight_id))
        db_flight = result.scalar_one_or_none()
        if not db_flight:
            return None

        db_flight.status = not db_flight.status
        await db.commit()
        await db.refresh(db_flight)
        return db_flight
