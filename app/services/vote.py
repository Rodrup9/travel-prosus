from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.vote import Vote
from app.schemas.vote import VoteCreate, VoteUpdate
from uuid import UUID

async def create_vote(session: AsyncSession, data: VoteCreate) -> Vote:
    vote = Vote(**data.dict())
    session.add(vote)
    await session.commit()
    await session.refresh(vote)
    return vote

async def get_vote(session: AsyncSession, vote_id: UUID) -> Vote | None:
    result = await session.execute(select(Vote).where(Vote.id == vote_id))
    return result.scalar_one_or_none()

async def get_all_votes(session: AsyncSession) -> list[Vote]:
    result = await session.execute(select(Vote))
    return result.scalars().all()

async def get_votes_by_trip(session: AsyncSession, trip_id: UUID) -> list[Vote]:
    result = await session.execute(select(Vote).where(Vote.trip_id == trip_id))
    return result.scalars().all()

async def get_votes_by_user(session: AsyncSession, user_id: UUID) -> list[Vote]:
    result = await session.execute(select(Vote).where(Vote.user_id == user_id))
    return result.scalars().all()

async def update_vote(session: AsyncSession, vote_id: UUID, data: VoteUpdate) -> Vote | None:
    vote = await get_vote(session, vote_id)
    if not vote:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(vote, key, value)
    session.add(vote)
    await session.commit()
    await session.refresh(vote)
    return vote

async def delete_vote(session: AsyncSession, vote_id: UUID) -> bool:
    vote = await get_vote(session, vote_id)
    if not vote:
        return False
    await session.delete(vote)
    await session.commit()
    return True
