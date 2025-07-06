from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from typing import List
import uuid

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = UserService.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = UserService.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@router.get("/", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    try:
        db_user = UserService.update_user(db, user_id, user_update)
        if not db_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.patch("/{user_id}/toggle-status", response_model=UserResponse)
async def toggle_user_status(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = UserService.toggle_user_status(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = UserService.get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user