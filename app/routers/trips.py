# app/routers/trip_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.services.trip import TripService
from app.database import get_db
from typing import List
import uuid

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    try:
        return TripService.create_trip(db, trip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TripResponse])
def get_all_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return TripService.get_all_trips(db, skip, limit)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip_by_id(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    trip = TripService.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: uuid.UUID, trip: TripUpdate, db: Session = Depends(get_db)):
    updated = TripService.update_trip(db, trip_id, trip)
    if not updated:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return updated


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = TripService.delete_trip(db, trip_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")


@router.patch("/{trip_id}/toggle-status", response_model=TripResponse)
def toggle_trip_status(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    trip = TripService.toggle_status(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip
