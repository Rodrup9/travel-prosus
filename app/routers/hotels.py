# app/routers/hotel_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.hotel import HotelCreate, HotelUpdate, HotelResponse
from app.services.hotel import HotelService
from app.database import get_db
from typing import List
import uuid

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.post("/", response_model=HotelResponse)
def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db)):
    try:
        return HotelService.create_hotel(db, hotel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[HotelResponse])
def get_all_hotels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return HotelService.get_hotels(db, skip, limit)


@router.get("/{hotel_id}", response_model=HotelResponse)
def get_hotel_by_id(hotel_id: uuid.UUID, db: Session = Depends(get_db)):
    hotel = HotelService.get_hotel_by_id(db, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return hotel


@router.get("/trip/{trip_id}", response_model=List[HotelResponse])
def get_hotels_by_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return HotelService.get_hotels_by_trip(db, trip_id)


@router.put("/{hotel_id}", response_model=HotelResponse)
def update_hotel(hotel_id: uuid.UUID, hotel_update: HotelUpdate, db: Session = Depends(get_db)):
    hotel = HotelService.update_hotel(db, hotel_id, hotel_update)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return hotel


@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = HotelService.delete_hotel(db, hotel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return {"message": "Hotel eliminado correctamente"}


@router.patch("/{hotel_id}/toggle-status", response_model=HotelResponse)
def toggle_hotel_status(hotel_id: uuid.UUID, db: Session = Depends(get_db)):
    hotel = HotelService.toggle_hotel_status(db, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return hotel
