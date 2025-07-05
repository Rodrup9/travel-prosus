from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Reemplaza esto con tu sesión async real
from app.database import async_session

# TODO: Crear modelo Trip en app/models/trip.py
# Estructura sugerida:
# class Trip(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     group_id: UUID = Field(foreign_key="group.id")
#     destination: str
#     start_date: date
#     end_date: date
#     status: bool = True

# Reemplaza esto con tus esquemas reales
# from app.schemas.trip import TripCreate, TripRead, TripUpdate

# Reemplaza esto con tus servicios reales
# from app.services.trip import (
#     create_trip,
#     get_trip,
#     get_all_trips,
#     get_trips_by_group,
#     update_trip,
#     delete_trip,
# )

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/")  # TODO: Agregar response_model=TripRead
async def create(data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por TripCreate
    """
    Crear un nuevo viaje.
    Requiere: group_id, destination, start_date, end_date
    """
    # TODO: return await create_trip(session, data)
    raise HTTPException(status_code=501, detail="Implementar create_trip service")

@router.get("/")  # TODO: Agregar response_model=list[TripRead]
async def read_all(session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los viajes.
    """
    # TODO: return await get_all_trips(session)
    raise HTTPException(status_code=501, detail="Implementar get_all_trips service")

@router.get("/group/{group_id}")  # TODO: Agregar response_model=list[TripRead]
async def read_by_group(group_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los viajes de un grupo específico.
    """
    # TODO: return await get_trips_by_group(session, group_id)
    raise HTTPException(status_code=501, detail="Implementar get_trips_by_group service")

@router.get("/{trip_id}")  # TODO: Agregar response_model=TripRead
async def read(trip_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener un viaje específico por ID.
    """
    # TODO: Implementar get_trip service
    # trip = await get_trip(session, trip_id)
    # if not trip:
    #     raise HTTPException(status_code=404, detail="Viaje no encontrado")
    # return trip
    raise HTTPException(status_code=501, detail="Implementar get_trip service")

@router.put("/{trip_id}")  # TODO: Agregar response_model=TripRead
async def update(trip_id: UUID, data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por TripUpdate
    """
    Actualizar un viaje existente.
    Permite actualizar: destination, start_date, end_date, status
    """
    # TODO: Implementar update_trip service
    # trip = await update_trip(session, trip_id, data)
    # if not trip:
    #     raise HTTPException(status_code=404, detail="Viaje no encontrado")
    # return trip
    raise HTTPException(status_code=501, detail="Implementar update_trip service")

@router.delete("/{trip_id}")
async def delete(trip_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Eliminar un viaje.
    """
    # TODO: Implementar delete_trip service
    # success = await delete_trip(session, trip_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Viaje no encontrado")
    # return {"ok": True}
    raise HTTPException(status_code=501, detail="Implementar delete_trip service")
