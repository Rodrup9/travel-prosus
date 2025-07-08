# app/routers/trip_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.schemas.trip import TripCreate, TripUpdate, TripResponse
from app.services.trip import TripService
from app.database import get_db

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("/", response_model=TripResponse)
async def create_trip(trip: TripCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await TripService.create_trip(db, trip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TripResponse])
async def get_all_trips(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await TripService.get_trips(db, skip=skip, limit=limit)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip_by_id(trip_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    trip = await TripService.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip


@router.get("/group/{group_id}", response_model=List[TripResponse])
async def get_trips_by_group(group_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await TripService.get_trips_by_group(db, group_id)


@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(trip_id: uuid.UUID, trip_update: TripUpdate, db: AsyncSession = Depends(get_db)):
    updated_trip = await TripService.update_trip(db, trip_id, trip_update)
    if not updated_trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return updated_trip


@router.delete("/{trip_id}")
async def delete_trip(trip_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await TripService.delete_trip(db, trip_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return {"message": "Viaje eliminado correctamente"}


@router.patch("/{trip_id}/toggle-status", response_model=TripResponse)
async def toggle_status(trip_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    trip = await TripService.toggle_status(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip
