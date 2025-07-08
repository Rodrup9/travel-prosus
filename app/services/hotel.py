# app/services/hotel_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate, HotelUpdate, HotelCreateCascade
from typing import List, Optional
import uuid


class HotelService:

    @staticmethod
    async def create_hotel(db: AsyncSession, hotel: HotelCreate) -> Hotel:
        db_hotel = Hotel(
            id=uuid.uuid4(),
            trip_id=hotel.trip_id,
            name=hotel.name,
            location=hotel.location,
            price_per_night=hotel.price_per_night,
            rating=hotel.rating,
            link=hotel.link,
            status=hotel.status,
        )
        try:
            db.add(db_hotel)
            await db.commit()
            await db.refresh(db_hotel)
            return db_hotel
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error al crear hotel. Verifica la relación trip_id.")
        
    @staticmethod
    async def create_hotel_cascade(db: AsyncSession, hotel: HotelCreateCascade, trip_id: uuid.UUID) -> Hotel:
        db_hotel = Hotel(
            id=uuid.uuid4(),
            trip_id=trip_id,
            name=hotel.name,
            location=hotel.location,
            price_per_night=hotel.price_per_night,
            rating=hotel.rating,
            link=hotel.link,
            status=hotel.status,
        )
        try:
            db.add(db_hotel)
            await db.commit()
            await db.refresh(db_hotel)
            return db_hotel
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error al crear hotel. Verifica la relación trip_id.")

    @staticmethod
    async def get_hotel_by_id(db: AsyncSession, hotel_id: uuid.UUID) -> Optional[Hotel]:
        result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_hotels(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Hotel]:
        result = await db.execute(select(Hotel).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_hotels_by_trip(db: AsyncSession, trip_id: uuid.UUID) -> List[Hotel]:
        result = await db.execute(select(Hotel).filter(Hotel.trip_id == trip_id))
        return result.scalars().all()

    @staticmethod
    async def update_hotel(db: AsyncSession, hotel_id: uuid.UUID, hotel_update: HotelUpdate) -> Optional[Hotel]:
        result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
        db_hotel = result.scalar_one_or_none()
        if not db_hotel:
            return None

        for key, value in hotel_update.dict(exclude_unset=True).items():
            setattr(db_hotel, key, value)

        await db.commit()
        await db.refresh(db_hotel)
        return db_hotel

    @staticmethod
    async def delete_hotel(db: AsyncSession, hotel_id: uuid.UUID) -> bool:
        result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
        db_hotel = result.scalar_one_or_none()
        if not db_hotel:
            return False

        await db.delete(db_hotel)
        await db.commit()
        return True

    @staticmethod
    async def toggle_status(db: AsyncSession, hotel_id: uuid.UUID) -> Optional[Hotel]:
        result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
        db_hotel = result.scalar_one_or_none()
        if not db_hotel:
            return None

        db_hotel.status = not db_hotel.status
        await db.commit()
        await db.refresh(db_hotel)
        return db_hotel
