# app/routers/itinerary_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.itinerary import ItineraryService
from app.schemas.itinerary import ItineraryCreate, ItineraryUpdate, ItineraryResponse
from typing import List
import uuid

router = APIRouter(prefix="/itineraries", tags=["Itineraries"])


@router.post("/", response_model=ItineraryResponse)
def create_itinerary(data: ItineraryCreate, db: Session = Depends(get_db)):
    try:
        return ItineraryService.create_itinerary(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ItineraryResponse])
def get_all_itineraries(db: Session = Depends(get_db)):
    return ItineraryService.get_all(db)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def get_itinerary_by_id(itinerary_id: uuid.UUID, db: Session = Depends(get_db)):
    itinerary = ItineraryService.get_by_id(db, itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return itinerary


@router.get("/trip/{trip_id}", response_model=List[ItineraryResponse])
def get_itineraries_by_trip_id(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return ItineraryService.get_by_trip_id(db, trip_id)


@router.put("/{itinerary_id}", response_model=ItineraryResponse)
def update_itinerary(itinerary_id: uuid.UUID, update: ItineraryUpdate, db: Session = Depends(get_db)):
    itinerary = ItineraryService.update_itinerary(db, itinerary_id, update)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return itinerary


@router.delete("/{itinerary_id}")
def delete_itinerary(itinerary_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = ItineraryService.delete_itinerary(db, itinerary_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return {"message": "Itinerario eliminado correctamente"}


@router.patch("/{itinerary_id}/toggle-status", response_model=ItineraryResponse)
def toggle_itinerary_status(itinerary_id: uuid.UUID, db: Session = Depends(get_db)):
    itinerary = ItineraryService.toggle_status(db, itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return itinerary
