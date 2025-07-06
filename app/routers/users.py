from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import async_session
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user import (
    create_user,
    get_user,
    get_all_users,
    update_user,
    delete_user,
)
from uuid import UUID

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/", response_model=UserRead)
async def create(data: UserCreate, session: AsyncSession = Depends(get_session)):
    return await create_user(session, data)

@router.get("/", response_model=list[UserRead])
async def read_all(session: AsyncSession = Depends(get_session)):
    return await get_all_users(session)

@router.get("/{user_id}", response_model=UserRead)
async def read(user_id: UUID, session: AsyncSession = Depends(get_session)):
    user = await get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/{user_id}", response_model=UserRead)
async def update(user_id: UUID, data: UserUpdate, session: AsyncSession = Depends(get_session)):
    user = await update_user(session, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.delete("/{user_id}")
async def delete(user_id: UUID, session: AsyncSession = Depends(get_session)):
    success = await delete_user(session, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"ok": True}
