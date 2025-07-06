# app/routers/flight_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.schemas.flight import FlightCreate, FlightUpdate, FlightResponse
from app.services.flight import FlightService
from app.database import get_db

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.post("/", response_model=FlightResponse)
def create_flight(flight: FlightCreate, db: Session = Depends(get_db)):
    try:
        return FlightService.create_flight(db, flight)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[FlightResponse])
def get_all_flights(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return FlightService.get_flights(db, skip=skip, limit=limit)


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight_by_id(flight_id: uuid.UUID, db: Session = Depends(get_db)):
    flight = FlightService.get_flight_by_id(db, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return flight


@router.get("/trip/{trip_id}", response_model=List[FlightResponse])
def get_flights_by_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return FlightService.get_flights_by_trip(db, trip_id)


@router.put("/{flight_id}", response_model=FlightResponse)
def update_flight(flight_id: uuid.UUID, flight_update: FlightUpdate, db: Session = Depends(get_db)):
    updated_flight = FlightService.update_flight(db, flight_id, flight_update)
    if not updated_flight:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return updated_flight


@router.delete("/{flight_id}")
def delete_flight(flight_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = FlightService.delete_flight(db, flight_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return {"message": "Vuelo eliminado correctamente"}


@router.patch("/{flight_id}/toggle-status", response_model=FlightResponse)
def toggle_status(flight_id: uuid.UUID, db: Session = Depends(get_db)):
    flight = FlightService.toggle_status(db, flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return flight
