# app/routers/hotel_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.schemas.hotel import HotelCreate, HotelUpdate, HotelResponse
from app.services.hotel import HotelService
from app.database import get_db

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.post("/", response_model=HotelResponse)
async def create_hotel(hotel: HotelCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await HotelService.create_hotel(db, hotel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[HotelResponse])
async def get_all_hotels(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await HotelService.get_hotels(db, skip=skip, limit=limit)


@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel_by_id(hotel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    hotel = await HotelService.get_hotel_by_id(db, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return hotel


@router.get("/trip/{trip_id}", response_model=List[HotelResponse])
async def get_hotels_by_trip(trip_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await HotelService.get_hotels_by_trip(db, trip_id)


@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(hotel_id: uuid.UUID, hotel_update: HotelUpdate, db: AsyncSession = Depends(get_db)):
    updated_hotel = await HotelService.update_hotel(db, hotel_id, hotel_update)
    if not updated_hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return updated_hotel


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await HotelService.delete_hotel(db, hotel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return {"message": "Hotel eliminado correctamente"}


@router.patch("/{hotel_id}/toggle-status", response_model=HotelResponse)
async def toggle_status(hotel_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    hotel = await HotelService.toggle_status(db, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel no encontrado")
    return hotel
