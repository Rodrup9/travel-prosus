from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate
from uuid import UUID

async def create_trip(session: AsyncSession, data: TripCreate) -> Trip:
    trip = Trip(**data.dict())
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip

async def get_trip(session: AsyncSession, trip_id: UUID) -> Trip | None:
    result = await session.execute(select(Trip).where(Trip.id == trip_id))
    return result.scalar_one_or_none()

async def get_all_trips(session: AsyncSession) -> list[Trip]:
    result = await session.execute(select(Trip))
    return result.scalars().all()

async def get_trips_by_group(session: AsyncSession, group_id: UUID) -> list[Trip]:
    result = await session.execute(select(Trip).where(Trip.group_id == group_id))
    return result.scalars().all()

async def update_trip(session: AsyncSession, trip_id: UUID, data: TripUpdate) -> Trip | None:
    trip = await get_trip(session, trip_id)
    if not trip:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(trip, key, value)
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip

async def delete_trip(session: AsyncSession, trip_id: UUID) -> bool:
    trip = await get_trip(session, trip_id)
    if not trip:
        return False
    await session.delete(trip)
    await session.commit()
    return True
