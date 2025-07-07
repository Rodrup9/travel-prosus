# app/services/flight_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.flight import Flight
from app.schemas.flight import FlightCreate, FlightUpdate
from typing import Optional, List
import uuid


class FlightService:

    @staticmethod
    def create_flight(db: Session, flight: FlightCreate) -> Flight:
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
            db.commit()
            db.refresh(db_flight)
            return db_flight
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al crear el vuelo: {str(e.orig)}")

    @staticmethod
    def get_flight_by_id(db: Session, flight_id: uuid.UUID) -> Optional[Flight]:
        return db.query(Flight).filter(Flight.id == flight_id).first()

    @staticmethod
    def get_flights(db: Session, skip: int = 0, limit: int = 100) -> List[Flight]:
        return db.query(Flight).offset(skip).limit(limit).all()

    @staticmethod
    def get_flights_by_trip(db: Session, trip_id: uuid.UUID) -> List[Flight]:
        return db.query(Flight).filter(Flight.trip_id == trip_id).all()

    @staticmethod
    def update_flight(db: Session, flight_id: uuid.UUID, update_data: FlightUpdate) -> Optional[Flight]:
        db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not db_flight:
            return None

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_flight, field, value)

        try:
            db.commit()
            db.refresh(db_flight)
            return db_flight
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al actualizar el vuelo: {str(e.orig)}")

    @staticmethod
    def delete_flight(db: Session, flight_id: uuid.UUID) -> bool:
        db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not db_flight:
            return False

        db.delete(db_flight)
        db.commit()
        return True

    @staticmethod
    def toggle_status(db: Session, flight_id: uuid.UUID) -> Optional[Flight]:
        db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not db_flight:
            return None

        db_flight.status = not db_flight.status
        db.commit()
        db.refresh(db_flight)
        return db_flight
