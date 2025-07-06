from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.itinerary import Itinerary
from app.schemas.itinerary import ItineraryCreate, ItineraryUpdate
from uuid import UUID
from datetime import date

async def create_itinerary(session: AsyncSession, data: ItineraryCreate) -> Itinerary:
    itinerary = Itinerary(**data.dict())
    session.add(itinerary)
    await session.commit()
    await session.refresh(itinerary)
    return itinerary

async def get_itinerary(session: AsyncSession, itinerary_id: UUID) -> Itinerary | None:
    result = await session.execute(select(Itinerary).where(Itinerary.id == itinerary_id))
    return result.scalar_one_or_none()

async def get_all_itineraries(session: AsyncSession) -> list[Itinerary]:
    result = await session.execute(select(Itinerary))
    return result.scalars().all()

async def get_itineraries_by_trip(session: AsyncSession, trip_id: UUID) -> list[Itinerary]:
    result = await session.execute(select(Itinerary).where(Itinerary.trip_id == trip_id))
    return result.scalars().all()

async def get_itineraries_by_day(session: AsyncSession, trip_id: UUID, day: date) -> list[Itinerary]:
    result = await session.execute(select(Itinerary).where(Itinerary.trip_id == trip_id, Itinerary.day == day))
    return result.scalars().all()

async def update_itinerary(session: AsyncSession, itinerary_id: UUID, data: ItineraryUpdate) -> Itinerary | None:
    itinerary = await get_itinerary(session, itinerary_id)
    if not itinerary:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(itinerary, key, value)
    session.add(itinerary)
    await session.commit()
    await session.refresh(itinerary)
    return itinerary

async def delete_itinerary(session: AsyncSession, itinerary_id: UUID) -> bool:
    itinerary = await get_itinerary(session, itinerary_id)
    if not itinerary:
        return False
    await session.delete(itinerary)
    await session.commit()
    return True
