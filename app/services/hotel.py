# app/services/hotel_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate, HotelUpdate
from typing import List, Optional
import uuid


class HotelService:

    @staticmethod
    def create_hotel(db: Session, hotel: HotelCreate) -> Hotel:
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
            db.commit()
            db.refresh(db_hotel)
            return db_hotel
        except IntegrityError:
            db.rollback()
            raise ValueError("Error al crear hotel. Verifica la relación trip_id.")

    @staticmethod
    def get_hotel_by_id(db: Session, hotel_id: uuid.UUID) -> Optional[Hotel]:
        return db.query(Hotel).filter(Hotel.id == hotel_id).first()

    @staticmethod
    def get_hotels(db: Session, skip: int = 0, limit: int = 100) -> List[Hotel]:
        return db.query(Hotel).offset(skip).limit(limit).all()

    @staticmethod
    def get_hotels_by_trip(db: Session, trip_id: uuid.UUID) -> List[Hotel]:
        return db.query(Hotel).filter(Hotel.trip_id == trip_id).all()

    @staticmethod
    def update_hotel(db: Session, hotel_id: uuid.UUID, hotel_update: HotelUpdate) -> Optional[Hotel]:
        db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not db_hotel:
            return None

        for key, value in hotel_update.dict(exclude_unset=True).items():
            setattr(db_hotel, key, value)

        db.commit()
        db.refresh(db_hotel)
        return db_hotel

    @staticmethod
    def delete_hotel(db: Session, hotel_id: uuid.UUID) -> bool:
        db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not db_hotel:
            return False

        db.delete(db_hotel)
        db.commit()
        return True

    @staticmethod
    def toggle_hotel_status(db: Session, hotel_id: uuid.UUID) -> Optional[Hotel]:
        db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not db_hotel:
            return None

        db_hotel.status = not db_hotel.status
        db.commit()
        db.refresh(db_hotel)
        return db_hotel
