# app/services/vote_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.vote import Vote
from app.schemas.vote import VoteCreate, VoteUpdate
from typing import Optional, List
import uuid

class VoteService:

    @staticmethod
    async def create_vote(db: AsyncSession, vote: VoteCreate) -> Vote:
        db_vote = Vote(
            id=uuid.uuid4(),
            trip_id=vote.trip_id,
            user_id=vote.user_id,
            vote=vote.vote,
            comment=vote.comment,
            status=vote.status
        )
        try:
            db.add(db_vote)
            await db.commit()
            await db.refresh(db_vote)
            return db_vote
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear voto: {str(e.orig)}")

    @staticmethod
    async def get_vote_by_id(db: AsyncSession, vote_id: uuid.UUID) -> Optional[Vote]:
        result = await db.execute(select(Vote).filter(Vote.id == vote_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_votes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Vote]:
        result = await db.execute(select(Vote).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_vote(db: AsyncSession, vote_id: uuid.UUID, vote_update: VoteUpdate) -> Optional[Vote]:
        result = await db.execute(select(Vote).filter(Vote.id == vote_id))
        db_vote = result.scalar_one_or_none()
        if not db_vote:
            return None

        for key, value in vote_update.dict(exclude_unset=True).items():
            setattr(db_vote, key, value)

        try:
            await db.commit()
            await db.refresh(db_vote)
            return db_vote
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al actualizar voto: {str(e.orig)}")

    @staticmethod
    async def delete_vote(db: AsyncSession, vote_id: uuid.UUID) -> bool:
        result = await db.execute(select(Vote).filter(Vote.id == vote_id))
        db_vote = result.scalar_one_or_none()
        if not db_vote:
            return False

        await db.delete(db_vote)
        await db.commit()
        return True

    @staticmethod
    async def toggle_status(db: AsyncSession, vote_id: uuid.UUID) -> Optional[Vote]:
        result = await db.execute(select(Vote).filter(Vote.id == vote_id))
        db_vote = result.scalar_one_or_none()
        if not db_vote:
            return None

        db_vote.status = not db_vote.status
        await db.commit()
        await db.refresh(db_vote)
        return db_vote

    @staticmethod
    async def get_votes_by_trip(db: AsyncSession, trip_id: uuid.UUID) -> List[Vote]:
        result = await db.execute(select(Vote).filter(Vote.trip_id == trip_id))
        return result.scalars().all()

    @staticmethod
    async def get_votes_by_user(db: AsyncSession, user_id: uuid.UUID) -> List[Vote]:
        result = await db.execute(select(Vote).filter(Vote.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def get_votes_by_user_and_trip(db: AsyncSession, user_id: uuid.UUID, trip_id: uuid.UUID) -> List[Vote]:
        result = await db.execute(select(Vote).filter(Vote.user_id == user_id, Vote.trip_id == trip_id))
        return result.scalars().all()
