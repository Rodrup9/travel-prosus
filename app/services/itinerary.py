# app/services/itinerary_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.itinerary import Itinerary
from app.schemas.itinerary import ItineraryCreate, ItineraryUpdate
from typing import List, Optional
import uuid


class ItineraryService:

    @staticmethod
    def create_itinerary(db: Session, data: ItineraryCreate) -> Itinerary:
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
            db.commit()
            db.refresh(itinerary)
            return itinerary
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al crear el itinerario: {str(e.orig)}")

    @staticmethod
    def get_all(db: Session) -> List[Itinerary]:
        return db.query(Itinerary).all()

    @staticmethod
    def get_by_id(db: Session, itinerary_id: uuid.UUID) -> Optional[Itinerary]:
        return db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()

    @staticmethod
    def get_by_trip_id(db: Session, trip_id: uuid.UUID) -> List[Itinerary]:
        return db.query(Itinerary).filter(Itinerary.trip_id == trip_id).all()

    @staticmethod
    def update_itinerary(db: Session, itinerary_id: uuid.UUID, update: ItineraryUpdate) -> Optional[Itinerary]:
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
        if not itinerary:
            return None

        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(itinerary, key, value)

        try:
            db.commit()
            db.refresh(itinerary)
            return itinerary
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al actualizar el itinerario: {str(e.orig)}")

    @staticmethod
    def delete_itinerary(db: Session, itinerary_id: uuid.UUID) -> bool:
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
        if not itinerary:
            return False
        db.delete(itinerary)
        db.commit()
        return True

    @staticmethod
    def toggle_status(db: Session, itinerary_id: uuid.UUID) -> Optional[Itinerary]:
        itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
        if not itinerary:
            return None
        itinerary.status = not itinerary.status
        db.commit()
        db.refresh(itinerary)
        return itinerary
