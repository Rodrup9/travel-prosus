from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Reemplaza esto con tu sesión async real
from app.database import async_session

# TODO: Crear modelo Hotel en app/models/hotel.py
# Estructura sugerida:
# class Hotel(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     trip_id: UUID = Field(foreign_key="trip.id")
#     name: str
#     location: str
#     price_per_night: float
#     rating: float
#     link: str
#     status: bool = True

# Reemplaza esto con tus esquemas reales
# from app.schemas.hotel import HotelCreate, HotelRead, HotelUpdate

# Reemplaza esto con tus servicios reales
# from app.services.hotel import (
#     create_hotel,
#     get_hotel,
#     get_all_hotels,
#     get_hotels_by_trip,
#     get_hotels_by_rating,
#     update_hotel,
#     delete_hotel,
# )

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/")  # TODO: Agregar response_model=HotelRead
async def create(data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por HotelCreate
    """
    Crear un nuevo hotel.
    Requiere: trip_id, name, location, price_per_night, rating, link
    """
    # TODO: return await create_hotel(session, data)
    raise HTTPException(status_code=501, detail="Implementar create_hotel service")

@router.get("/")  # TODO: Agregar response_model=list[HotelRead]
async def read_all(session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los hoteles.
    """
    # TODO: return await get_all_hotels(session)
    raise HTTPException(status_code=501, detail="Implementar get_all_hotels service")

@router.get("/trip/{trip_id}")  # TODO: Agregar response_model=list[HotelRead]
async def read_by_trip(trip_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los hoteles de un viaje específico.
    """
    # TODO: return await get_hotels_by_trip(session, trip_id)
    raise HTTPException(status_code=501, detail="Implementar get_hotels_by_trip service")

@router.get("/rating/{min_rating}")  # TODO: Agregar response_model=list[HotelRead]
async def read_by_rating(min_rating: float, session: AsyncSession = Depends(get_session)):
    """
    Obtener hoteles con calificación mínima específica.
    """
    # TODO: return await get_hotels_by_rating(session, min_rating)
    raise HTTPException(status_code=501, detail="Implementar get_hotels_by_rating service")

@router.get("/{hotel_id}")  # TODO: Agregar response_model=HotelRead
async def read(hotel_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener un hotel específico por ID.
    """
    # TODO: Implementar get_hotel service
    # hotel = await get_hotel(session, hotel_id)
    # if not hotel:
    #     raise HTTPException(status_code=404, detail="Hotel no encontrado")
    # return hotel
    raise HTTPException(status_code=501, detail="Implementar get_hotel service")

@router.put("/{hotel_id}")  # TODO: Agregar response_model=HotelRead
async def update(hotel_id: UUID, data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por HotelUpdate
    """
    Actualizar un hotel existente.
    Permite actualizar: name, location, price_per_night, rating, link, status
    """
    # TODO: Implementar update_hotel service
    # hotel = await update_hotel(session, hotel_id, data)
    # if not hotel:
    #     raise HTTPException(status_code=404, detail="Hotel no encontrado")
    # return hotel
    raise HTTPException(status_code=501, detail="Implementar update_hotel service")

@router.delete("/{hotel_id}")
async def delete(hotel_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Eliminar un hotel.
    """
    # TODO: Implementar delete_hotel service
    # success = await delete_hotel(session, hotel_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Hotel no encontrado")
    # return {"ok": True}
    raise HTTPException(status_code=501, detail="Implementar delete_hotel service")
