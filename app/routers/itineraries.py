from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Reemplaza esto con tu sesión async real
from app.database import async_session

# TODO: Crear modelo Itinerary en app/models/itinerary.py
# Estructura sugerida:
# class Itinerary(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     trip_id: UUID = Field(foreign_key="trip.id")
#     day: date
#     activity: str
#     location: str
#     start_time: time
#     end_time: time
#     status: bool = True

# Reemplaza esto con tus esquemas reales
# from app.schemas.itinerary import ItineraryCreate, ItineraryRead, ItineraryUpdate

# Reemplaza esto con tus servicios reales
# from app.services.itinerary import (
#     create_itinerary,
#     get_itinerary,
#     get_all_itineraries,
#     get_itineraries_by_trip,
#     get_itineraries_by_day,
#     update_itinerary,
#     delete_itinerary,
# )

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/")  # TODO: Agregar response_model=ItineraryRead
async def create(data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por ItineraryCreate
    """
    Crear un nuevo itinerario.
    Requiere: trip_id, day, activity, location, start_time, end_time
    """
    # TODO: return await create_itinerary(session, data)
    raise HTTPException(status_code=501, detail="Implementar create_itinerary service")

@router.get("/")  # TODO: Agregar response_model=list[ItineraryRead]
async def read_all(session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los itinerarios.
    """
    # TODO: return await get_all_itineraries(session)
    raise HTTPException(status_code=501, detail="Implementar get_all_itineraries service")

@router.get("/trip/{trip_id}")  # TODO: Agregar response_model=list[ItineraryRead]
async def read_by_trip(trip_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los itinerarios de un viaje específico.
    """
    # TODO: return await get_itineraries_by_trip(session, trip_id)
    raise HTTPException(status_code=501, detail="Implementar get_itineraries_by_trip service")

@router.get("/trip/{trip_id}/day/{day}")  # TODO: Agregar response_model=list[ItineraryRead]
async def read_by_day(trip_id: UUID, day: str, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar str por date
    """
    Obtener todos los itinerarios de un día específico de un viaje.
    """
    # TODO: return await get_itineraries_by_day(session, trip_id, day)
    raise HTTPException(status_code=501, detail="Implementar get_itineraries_by_day service")

@router.get("/{itinerary_id}")  # TODO: Agregar response_model=ItineraryRead
async def read(itinerary_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener un itinerario específico por ID.
    """
    # TODO: Implementar get_itinerary service
    # itinerary = await get_itinerary(session, itinerary_id)
    # if not itinerary:
    #     raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    # return itinerary
    raise HTTPException(status_code=501, detail="Implementar get_itinerary service")

@router.put("/{itinerary_id}")  # TODO: Agregar response_model=ItineraryRead
async def update(itinerary_id: UUID, data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por ItineraryUpdate
    """
    Actualizar un itinerario existente.
    Permite actualizar: day, activity, location, start_time, end_time, status
    """
    # TODO: Implementar update_itinerary service
    # itinerary = await update_itinerary(session, itinerary_id, data)
    # if not itinerary:
    #     raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    # return itinerary
    raise HTTPException(status_code=501, detail="Implementar update_itinerary service")

@router.delete("/{itinerary_id}")
async def delete(itinerary_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Eliminar un itinerario.
    """
    # TODO: Implementar delete_itinerary service
    # success = await delete_itinerary(session, itinerary_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Itinerario no encontrado")
    # return {"ok": True}
    raise HTTPException(status_code=501, detail="Implementar delete_itinerary service")
