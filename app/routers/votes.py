# app/routers/vote_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.schemas.vote import VoteCreate, VoteUpdate, VoteResponse
from app.services.vote import VoteService
from app.database import get_db

router = APIRouter(prefix="/votes", tags=["Votes"])


@router.post("/", response_model=VoteResponse)
async def create_vote(vote: VoteCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await VoteService.create_vote(db, vote)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[VoteResponse])
async def get_all_votes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await VoteService.get_votes(db, skip=skip, limit=limit)


@router.get("/{vote_id}", response_model=VoteResponse)
async def get_vote_by_id(vote_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    vote = await VoteService.get_vote_by_id(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    return vote


@router.get("/trip/{trip_id}", response_model=List[VoteResponse])
async def get_votes_by_trip(trip_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await VoteService.get_votes_by_trip(db, trip_id)


@router.put("/{vote_id}", response_model=VoteResponse)
async def update_vote(vote_id: uuid.UUID, vote_update: VoteUpdate, db: AsyncSession = Depends(get_db)):
    updated_vote = await VoteService.update_vote(db, vote_id, vote_update)
    if not updated_vote:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    return updated_vote


@router.delete("/{vote_id}")
async def delete_vote(vote_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await VoteService.delete_vote(db, vote_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    return {"message": "Voto eliminado correctamente"}


@router.patch("/{vote_id}/toggle-status", response_model=VoteResponse)
async def toggle_status(vote_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    vote = await VoteService.toggle_status(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Voto no encontrado")
    return vote
