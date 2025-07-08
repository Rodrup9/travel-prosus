# app/services/trip_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate
from app.services.itinerary import ItineraryService
from app.services.hotel import HotelService
from app.services.flight import FlightService
from typing import List, Optional
import uuid

class TripService:

    @staticmethod
    async def create_trip(db: AsyncSession, trip: TripCreate) -> Trip:
        db_trip = Trip(
            id=uuid.uuid4(),
            group_id=trip.group_id,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            status=trip.status
        )
        try:
            db.add(db_trip)
            await db.commit()
            await db.refresh(db_trip)
            return db_trip
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear el viaje: {str(e.orig)}")

    @staticmethod
    async def create_trip_cascade(db: AsyncSession, trip: TripCreate) -> Trip:
        db_trip = Trip(
            id=uuid.uuid4(),
            group_id=trip.group_id,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            status=trip.status
        )
        try:
            db.add(db_trip)
            await db.commit()
            await db.refresh(db_trip)
            for itinerary in trip.itineraries:
                await ItineraryService.create_itinerary_cascade(db, itinerary, db_trip.id)
            for hotel in trip.hotels:
                await HotelService.create_hotel_cascade(db, hotel, db_trip.id)
            for flight in trip.flights:
                await FlightService.create_flight_cascade(db, flight, db_trip.id)
            return db_trip
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear el viaje: {str(e.orig)}")

    @staticmethod
    async def get_trip_by_id(db: AsyncSession, trip_id: uuid.UUID) -> Optional[Trip]:
        result = await db.execute(select(Trip).filter(Trip.id == trip_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_trips(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Trip]:
        result = await db.execute(select(Trip).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_trips_by_group(db: AsyncSession, group_id: uuid.UUID) -> List[Trip]:
        result = await db.execute(select(Trip).filter(Trip.group_id == group_id))
        return result.scalars().all()

    @staticmethod
    async def update_trip(db: AsyncSession, trip_id: uuid.UUID, trip_data: TripUpdate) -> Optional[Trip]:
        result = await db.execute(select(Trip).filter(Trip.id == trip_id))
        db_trip = result.scalar_one_or_none()
        if not db_trip:
            return None

        update_data = trip_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_trip, field, value)

        try:
            await db.commit()
            await db.refresh(db_trip)
            return db_trip
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al actualizar el viaje: {str(e.orig)}")

    @staticmethod
    async def delete_trip(db: AsyncSession, trip_id: uuid.UUID) -> bool:
        result = await db.execute(select(Trip).filter(Trip.id == trip_id))
        db_trip = result.scalar_one_or_none()
        if not db_trip:
            return False

        await db.delete(db_trip)
        await db.commit()
        return True

    @staticmethod
    async def toggle_status(db: AsyncSession, trip_id: uuid.UUID) -> Optional[Trip]:
        result = await db.execute(select(Trip).filter(Trip.id == trip_id))
        db_trip = result.scalar_one_or_none()
        if not db_trip:
            return None

        db_trip.status = not db_trip.status
        await db.commit()
        await db.refresh(db_trip)
        return db_trip
