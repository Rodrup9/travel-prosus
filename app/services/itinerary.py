# app/services/itinerary_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.itinerary import Itinerary
from app.schemas.itinerary import ItineraryCreate, ItineraryUpdate
from typing import List, Optional
import uuid


class ItineraryService:

    @staticmethod
    async def create_itinerary(db: AsyncSession, data: ItineraryCreate) -> Itinerary:
        itinerary = Itinerary(
            id=uuid.uuid4(),
            trip_id=data.trip_id,
            day=data.day,
            activity=data.activity,
            location=data.location,
            start_time=data.start_time,
            end_time=data.end_time,
            status=data.status
        )
        try:
            db.add(itinerary)
            await db.commit()
            await db.refresh(itinerary)
            return itinerary
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear el itinerario: {str(e.orig)}")

    @staticmethod
    async def get_itineraries(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Itinerary]:
        result = await db.execute(select(Itinerary).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_itinerary_by_id(db: AsyncSession, itinerary_id: uuid.UUID) -> Optional[Itinerary]:
        result = await db.execute(select(Itinerary).filter(Itinerary.id == itinerary_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_itineraries_by_trip(db: AsyncSession, trip_id: uuid.UUID) -> List[Itinerary]:
        result = await db.execute(select(Itinerary).filter(Itinerary.trip_id == trip_id))
        return result.scalars().all()

    @staticmethod
    async def update_itinerary(db: AsyncSession, itinerary_id: uuid.UUID, update: ItineraryUpdate) -> Optional[Itinerary]:
        result = await db.execute(select(Itinerary).filter(Itinerary.id == itinerary_id))
        itinerary = result.scalar_one_or_none()
        if not itinerary:
            return None

        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(itinerary, key, value)

        try:
            await db.commit()
            await db.refresh(itinerary)
            return itinerary
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al actualizar el itinerario: {str(e.orig)}")

    @staticmethod
    async def delete_itinerary(db: AsyncSession, itinerary_id: uuid.UUID) -> bool:
        result = await db.execute(select(Itinerary).filter(Itinerary.id == itinerary_id))
        itinerary = result.scalar_one_or_none()
        if not itinerary:
            return False
        await db.delete(itinerary)
        await db.commit()
        return True

    @staticmethod
    async def toggle_status(db: AsyncSession, itinerary_id: uuid.UUID) -> Optional[Itinerary]:
        result = await db.execute(select(Itinerary).filter(Itinerary.id == itinerary_id))
        itinerary = result.scalar_one_or_none()
        if not itinerary:
            return None
        itinerary.status = not itinerary.status
        await db.commit()
        await db.refresh(itinerary)
        return itinerary
