# app/services/trip_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate
from typing import List, Optional
import uuid

class TripService:

    @staticmethod
    def create_trip(db: Session, trip: TripCreate) -> Trip:
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
            db.commit()
            db.refresh(db_trip)
            return db_trip
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al crear el viaje: {str(e.orig)}")

    @staticmethod
    def get_trip_by_id(db: Session, trip_id: uuid.UUID) -> Optional[Trip]:
        return db.query(Trip).filter(Trip.id == trip_id).first()

    @staticmethod
    def get_all_trips(db: Session, skip: int = 0, limit: int = 100) -> List[Trip]:
        return db.query(Trip).offset(skip).limit(limit).all()

    @staticmethod
    def update_trip(db: Session, trip_id: uuid.UUID, trip_data: TripUpdate) -> Optional[Trip]:
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not db_trip:
            return None

        update_data = trip_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_trip, field, value)

        try:
            db.commit()
            db.refresh(db_trip)
            return db_trip
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al actualizar el viaje: {str(e.orig)}")

    @staticmethod
    def delete_trip(db: Session, trip_id: uuid.UUID) -> bool:
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not db_trip:
            return False

        db.delete(db_trip)
        db.commit()
        return True

    @staticmethod
    def toggle_status(db: Session, trip_id: uuid.UUID) -> Optional[Trip]:
        db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not db_trip:
            return None

        db_trip.status = not db_trip.status
        db.commit()
        db.refresh(db_trip)
        return db_trip
