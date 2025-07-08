# app/routers/itinerary_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.schemas.itinerary import ItineraryCreate, ItineraryUpdate, ItineraryResponse
from app.services.itinerary import ItineraryService
from app.database import get_db

router = APIRouter(prefix="/itineraries", tags=["Itineraries"])


@router.post("/", response_model=ItineraryResponse)
async def create_itinerary(itinerary: ItineraryCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await ItineraryService.create_itinerary(db, itinerary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ItineraryResponse])
async def get_all_itineraries(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await ItineraryService.get_itineraries(db, skip=skip, limit=limit)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
async def get_itinerary_by_id(itinerary_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    itinerary = await ItineraryService.get_itinerary_by_id(db, itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return itinerary


@router.get("/trip/{trip_id}", response_model=List[ItineraryResponse])
async def get_itineraries_by_trip(trip_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await ItineraryService.get_itineraries_by_trip(db, trip_id)


@router.put("/{itinerary_id}", response_model=ItineraryResponse)
async def update_itinerary(itinerary_id: uuid.UUID, itinerary_update: ItineraryUpdate, db: AsyncSession = Depends(get_db)):
    updated_itinerary = await ItineraryService.update_itinerary(db, itinerary_id, itinerary_update)
    if not updated_itinerary:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return updated_itinerary


@router.delete("/{itinerary_id}")
async def delete_itinerary(itinerary_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await ItineraryService.delete_itinerary(db, itinerary_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return {"message": "Itinerario eliminado correctamente"}


@router.patch("/{itinerary_id}/toggle-status", response_model=ItineraryResponse)
async def toggle_status(itinerary_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    itinerary = await ItineraryService.toggle_status(db, itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    return itinerary
