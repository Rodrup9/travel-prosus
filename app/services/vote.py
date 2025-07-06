# app/services/vote_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.vote import Vote
from app.schemas.vote import VoteCreate, VoteUpdate
from typing import Optional, List
import uuid

class VoteService:

    @staticmethod
    def create_vote(db: Session, vote: VoteCreate) -> Vote:
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
            db.commit()
            db.refresh(db_vote)
            return db_vote
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al crear voto: {str(e.orig)}")

    @staticmethod
    def get_vote_by_id(db: Session, vote_id: uuid.UUID) -> Optional[Vote]:
        return db.query(Vote).filter(Vote.id == vote_id).first()

    @staticmethod
    def get_all_votes(db: Session, skip: int = 0, limit: int = 100) -> List[Vote]:
        return db.query(Vote).offset(skip).limit(limit).all()

    @staticmethod
    def update_vote(db: Session, vote_id: uuid.UUID, vote_update: VoteUpdate) -> Optional[Vote]:
        db_vote = db.query(Vote).filter(Vote.id == vote_id).first()
        if not db_vote:
            return None

        for key, value in vote_update.dict(exclude_unset=True).items():
            setattr(db_vote, key, value)

        try:
            db.commit()
            db.refresh(db_vote)
            return db_vote
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al actualizar voto: {str(e.orig)}")

    @staticmethod
    def delete_vote(db: Session, vote_id: uuid.UUID) -> bool:
        db_vote = db.query(Vote).filter(Vote.id == vote_id).first()
        if not db_vote:
            return False

        db.delete(db_vote)
        db.commit()
        return True

    @staticmethod
    def toggle_vote_status(db: Session, vote_id: uuid.UUID) -> Optional[Vote]:
        db_vote = db.query(Vote).filter(Vote.id == vote_id).first()
        if not db_vote:
            return None

        db_vote.status = not db_vote.status
        db.commit()
        db.refresh(db_vote)
        return db_vote

    @staticmethod
    def get_votes_by_trip(db: Session, trip_id: uuid.UUID) -> List[Vote]:
        return db.query(Vote).filter(Vote.trip_id == trip_id).all()

    @staticmethod
    def get_votes_by_user(db: Session, user_id: uuid.UUID) -> List[Vote]:
        return db.query(Vote).filter(Vote.user_id == user_id).all()

    @staticmethod
    def get_votes_by_user_and_trip(db: Session, user_id: uuid.UUID, trip_id: uuid.UUID) -> List[Vote]:
        return db.query(Vote).filter(Vote.user_id == user_id, Vote.trip_id == trip_id).all()
