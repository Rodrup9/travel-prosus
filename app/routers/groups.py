from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.schemas.group import GroupCreate, GroupUpdate, GroupOut
from app.services.group import GroupService
from app.database import get_db
from app.middleware.verify_session import get_verify_session
router = APIRouter(
    prefix="/groups",
    tags=["Groups"]
)

@router.post("/", response_model=GroupOut)
async def create_group(data: GroupCreate,current_user = Depends(get_verify_session), db: AsyncSession = Depends(get_db)):
    try:
        return await GroupService.create_group(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[GroupOut])
async def get_all_groups(db: AsyncSession = Depends(get_db)):
    return await GroupService.get_groups(db)

@router.get("/{group_id}", response_model=GroupOut)
async def get_group_by_id(group_id: UUID, db: AsyncSession = Depends(get_db)):
    group = await GroupService.get_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group

@router.get("/user/{user_id}", response_model=List[GroupOut])
async def get_groups_by_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await GroupService.get_by_user(db, user_id)

@router.put("/{group_id}", response_model=GroupOut)
async def update_group(group_id: UUID, update: GroupUpdate,current_user = Depends(get_verify_session), db: AsyncSession = Depends(get_db)):
    group = await GroupService.update_group(db, group_id, update)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group

@router.delete("/{group_id}")
async def delete_group(group_id: UUID,current_user = Depends(get_verify_session), db: AsyncSession = Depends(get_db)):
    success = await GroupService.delete_group(db, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return {"detail": "Grupo eliminado correctamente"}

@router.patch("/{group_id}/toggle-status", response_model=GroupOut)
async def toggle_group_status(group_id: UUID,current_user = Depends(get_verify_session), db: AsyncSession = Depends(get_db)):
    group = await GroupService.toggle_group_status(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group
