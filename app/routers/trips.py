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
    
@router.post("/full-creation", response_model=TripResponse)
async def create_trip_full(trip: TripCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await TripService.create_trip_cascade(db, trip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[TripResponse])
async def get_all_trips(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Obtener todos los trips con paginación
    """
    try:
        print(f"🔍 Obteniendo trips (skip: {skip}, limit: {limit})")
        
        trips = await TripService.get_trips(db, skip=skip, limit=limit)
        
        print(f"✅ Encontrados {len(trips)} trips")
        
        # Log de datos problemáticos
        for trip in trips:
            if trip.start_date is None or trip.end_date is None:
                print(f"⚠️ Trip {trip.id} tiene fechas NULL:")
                print(f"   - Start: {trip.start_date}")
                print(f"   - End: {trip.end_date}")
        
        return trips
        
    except Exception as e:
        print(f"❌ Error obteniendo todos los trips: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving trips: {str(e)}"
        )


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip_by_id(trip_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    trip = await TripService.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return trip


@router.get("/group/{group_id}", response_model=List[TripResponse])
async def get_trips_by_group(group_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Obtener todos los trips de un grupo específico
    """
    try:
        print(f"🔍 Buscando trips para grupo: {group_id}")
        
        trips = await TripService.get_trips_by_group(db, group_id)
        
        print(f"✅ Encontrados {len(trips)} trips para el grupo")
        
        # Validar datos antes de retornar
        for i, trip in enumerate(trips):
            print(f"Trip {i+1}:")
            print(f"  - ID: {trip.id}")
            print(f"  - Destination: {trip.destination}")
            print(f"  - Start Date: {trip.start_date}")  # Ahora puede ser None
            print(f"  - End Date: {trip.end_date}")      # Ahora puede ser None
            print(f"  - Status: {trip.status}")
        
        return trips
        
    except Exception as e:
        print(f"❌ Error obteniendo trips del grupo {group_id}: {str(e)}")
        print(f"Error type: {type(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving trips for group: {str(e)}"
        )


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


@router.get("/debug/validate-dates")
async def debug_validate_trip_dates(db: AsyncSession = Depends(get_db)):
    """
    Debug endpoint para verificar trips con fechas NULL
    """
    try:
        print("🧪 Verificando fechas de trips...")
        
        # Obtener todos los trips directamente sin validación de schema
        from sqlalchemy import select
        from app.models.trip import Trip
        
        result = await db.execute(select(Trip))
        raw_trips = result.scalars().all()
        
        problems = []
        valid_trips = []
        
        for trip in raw_trips:
            trip_info = {
                "id": str(trip.id),
                "destination": trip.destination,
                "start_date": trip.start_date,
                "end_date": trip.end_date,
                "status": trip.status
            }
            
            if trip.start_date is None or trip.end_date is None:
                problems.append({
                    **trip_info,
                    "issue": "NULL dates"
                })
            else:
                valid_trips.append(trip_info)
        
        result = {
            "total_trips": len(raw_trips),
            "valid_trips": len(valid_trips),
            "problematic_trips": len(problems),
            "problems": problems[:5],  # Solo primeros 5 para no saturar
            "status": "validation_complete"
        }
        
        print(f"📊 Resultados validación:")
        print(f"   - Total trips: {result['total_trips']}")
        print(f"   - Válidos: {result['valid_trips']}")
        print(f"   - Problemáticos: {result['problematic_trips']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error en validación: {str(e)}")
        return {
            "error": str(e),
            "status": "validation_failed"
        }
