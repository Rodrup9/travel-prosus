from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate, HotelUpdate
from uuid import UUID

async def create_hotel(session: AsyncSession, data: HotelCreate) -> Hotel:
    hotel = Hotel(**data.dict())
    session.add(hotel)
    await session.commit()
    await session.refresh(hotel)
    return hotel

async def get_hotel(session: AsyncSession, hotel_id: UUID) -> Hotel | None:
    result = await session.execute(select(Hotel).where(Hotel.id == hotel_id))
    return result.scalar_one_or_none()

async def get_all_hotels(session: AsyncSession) -> list[Hotel]:
    result = await session.execute(select(Hotel))
    return result.scalars().all()

async def get_hotels_by_trip(session: AsyncSession, trip_id: UUID) -> list[Hotel]:
    result = await session.execute(select(Hotel).where(Hotel.trip_id == trip_id))
    return result.scalars().all()

async def get_hotels_by_rating(session: AsyncSession, min_rating: float) -> list[Hotel]:
    result = await session.execute(select(Hotel).where(Hotel.rating >= min_rating))
    return result.scalars().all()

async def update_hotel(session: AsyncSession, hotel_id: UUID, data: HotelUpdate) -> Hotel | None:
    hotel = await get_hotel(session, hotel_id)
    if not hotel:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(hotel, key, value)
    session.add(hotel)
    await session.commit()
    await session.refresh(hotel)
    return hotel

async def delete_hotel(session: AsyncSession, hotel_id: UUID) -> bool:
    hotel = await get_hotel(session, hotel_id)
    if not hotel:
        return False
    await session.delete(hotel)
    await session.commit()
    return True
