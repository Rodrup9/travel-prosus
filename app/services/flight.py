from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.flight import Flight
from app.schemas.flight import FlightCreate, FlightUpdate
from uuid import UUID

async def create_flight(session: AsyncSession, data: FlightCreate) -> Flight:
    flight = Flight(**data.dict())
    session.add(flight)
    await session.commit()
    await session.refresh(flight)
    return flight

async def get_flight(session: AsyncSession, flight_id: UUID) -> Flight | None:
    result = await session.execute(select(Flight).where(Flight.id == flight_id))
    return result.scalar_one_or_none()

async def get_all_flights(session: AsyncSession) -> list[Flight]:
    result = await session.execute(select(Flight))
    return result.scalars().all()

async def get_flights_by_trip(session: AsyncSession, trip_id: UUID) -> list[Flight]:
    result = await session.execute(select(Flight).where(Flight.trip_id == trip_id))
    return result.scalars().all()

async def get_flights_by_airline(session: AsyncSession, airline: str) -> list[Flight]:
    result = await session.execute(select(Flight).where(Flight.airline == airline))
    return result.scalars().all()

async def get_flights_by_airport(session: AsyncSession, airport: str) -> list[Flight]:
    result = await session.execute(select(Flight).where(Flight.departure_airport == airport))
    return result.scalars().all()

async def update_flight(session: AsyncSession, flight_id: UUID, data: FlightUpdate) -> Flight | None:
    flight = await get_flight(session, flight_id)
    if not flight:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(flight, key, value)
    session.add(flight)
    await session.commit()
    await session.refresh(flight)
    return flight

async def delete_flight(session: AsyncSession, flight_id: UUID) -> bool:
    flight = await get_flight(session, flight_id)
    if not flight:
        return False
    await session.delete(flight)
    await session.commit()
    return True
