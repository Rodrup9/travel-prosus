from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Reemplaza esto con tu sesión async real
from app.database import async_session

# TODO: Crear modelo Flight en app/models/flight.py
# Estructura sugerida:
# class Flight(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     trip_id: UUID = Field(foreign_key="trip.id")
#     airline: str
#     departure_airport: str
#     arrival_time: datetime
#     price: float
#     status: bool = True

# Reemplaza esto con tus esquemas reales
# from app.schemas.flight import FlightCreate, FlightRead, FlightUpdate

# Reemplaza esto con tus servicios reales
# from app.services.flight import (
#     create_flight,
#     get_flight,
#     get_all_flights,
#     get_flights_by_trip,
#     get_flights_by_airline,
#     get_flights_by_airport,
#     update_flight,
#     delete_flight,
# )

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/")  # TODO: Agregar response_model=FlightRead
async def create(data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por FlightCreate
    """
    Crear un nuevo vuelo.
    Requiere: trip_id, airline, departure_airport, arrival_time, price
    """
    # TODO: return await create_flight(session, data)
    raise HTTPException(status_code=501, detail="Implementar create_flight service")

@router.get("/")  # TODO: Agregar response_model=list[FlightRead]
async def read_all(session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los vuelos.
    """
    # TODO: return await get_all_flights(session)
    raise HTTPException(status_code=501, detail="Implementar get_all_flights service")

@router.get("/trip/{trip_id}")  # TODO: Agregar response_model=list[FlightRead]
async def read_by_trip(trip_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los vuelos de un viaje específico.
    """
    # TODO: return await get_flights_by_trip(session, trip_id)
    raise HTTPException(status_code=501, detail="Implementar get_flights_by_trip service")

@router.get("/airline/{airline}")  # TODO: Agregar response_model=list[FlightRead]
async def read_by_airline(airline: str, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los vuelos de una aerolínea específica.
    """
    # TODO: return await get_flights_by_airline(session, airline)
    raise HTTPException(status_code=501, detail="Implementar get_flights_by_airline service")

@router.get("/airport/{airport}")  # TODO: Agregar response_model=list[FlightRead]
async def read_by_airport(airport: str, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los vuelos desde un aeropuerto específico.
    """
    # TODO: return await get_flights_by_airport(session, airport)
    raise HTTPException(status_code=501, detail="Implementar get_flights_by_airport service")

@router.get("/{flight_id}")  # TODO: Agregar response_model=FlightRead
async def read(flight_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener un vuelo específico por ID.
    """
    # TODO: Implementar get_flight service
    # flight = await get_flight(session, flight_id)
    # if not flight:
    #     raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    # return flight
    raise HTTPException(status_code=501, detail="Implementar get_flight service")

@router.put("/{flight_id}")  # TODO: Agregar response_model=FlightRead
async def update(flight_id: UUID, data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por FlightUpdate
    """
    Actualizar un vuelo existente.
    Permite actualizar: airline, departure_airport, arrival_time, price, status
    """
    # TODO: Implementar update_flight service
    # flight = await update_flight(session, flight_id, data)
    # if not flight:
    #     raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    # return flight
    raise HTTPException(status_code=501, detail="Implementar update_flight service")

@router.delete("/{flight_id}")
async def delete(flight_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Eliminar un vuelo.
    """
    # TODO: Implementar delete_flight service
    # success = await delete_flight(session, flight_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    # return {"ok": True}
    raise HTTPException(status_code=501, detail="Implementar delete_flight service")
