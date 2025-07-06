# app/routes/votes_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.schemas.vote import VoteCreate, VoteUpdate, VoteResponse
from app.services.vote import VoteService

router = APIRouter(prefix="/votes", tags=["Votes"])

@router.post("/", response_model=VoteResponse, status_code=status.HTTP_201_CREATED)
def create_vote(vote: VoteCreate, db: Session = Depends(get_db)):
    try:
        return VoteService.create_vote(db, vote)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[VoteResponse])
def get_all_votes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return VoteService.get_all_votes(db, skip, limit)

@router.get("/{vote_id}", response_model=VoteResponse)
def get_vote_by_id(vote_id: uuid.UUID, db: Session = Depends(get_db)):
    vote = VoteService.get_vote_by_id(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    return vote

@router.put("/{vote_id}", response_model=VoteResponse)
def update_vote(vote_id: uuid.UUID, vote_update: VoteUpdate, db: Session = Depends(get_db)):
    vote = VoteService.update_vote(db, vote_id, vote_update)
    if not vote:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    return vote

@router.delete("/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vote(vote_id: uuid.UUID, db: Session = Depends(get_db)):
    success = VoteService.delete_vote(db, vote_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voto no encontrado")

@router.patch("/{vote_id}/toggle", response_model=VoteResponse)
def toggle_vote_status(vote_id: uuid.UUID, db: Session = Depends(get_db)):
    vote = VoteService.toggle_vote_status(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    return vote

@router.get("/by-trip/{trip_id}", response_model=List[VoteResponse])
def get_votes_by_trip(trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return VoteService.get_votes_by_trip(db, trip_id)

@router.get("/by-user/{user_id}", response_model=List[VoteResponse])
def get_votes_by_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return VoteService.get_votes_by_user(db, user_id)

@router.get("/by-user-trip/", response_model=List[VoteResponse])
def get_votes_by_user_and_trip(user_id: uuid.UUID, trip_id: uuid.UUID, db: Session = Depends(get_db)):
    return VoteService.get_votes_by_user_and_trip(db, user_id, trip_id)
