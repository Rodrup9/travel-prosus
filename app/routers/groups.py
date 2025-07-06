from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Reemplaza esto con tu sesión async real
from app.database import async_session

# Reemplaza esto con tus esquemas reales
# from app.schemas.group import GroupCreate, GroupRead, GroupUpdate

# Reemplaza esto con tus servicios reales
# from app.services.group import (
#     create_group,
#     get_group,
#     get_all_groups,
#     update_group,
#     delete_group,
# )

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/", response_model="GroupRead")  # Reemplaza con: response_model=GroupRead
async def create(data: "GroupCreate", session: AsyncSession = Depends(get_session)):  # Reemplaza con: data: GroupCreate
    return await create_group(session, data)

@router.get("/", response_model=list["GroupRead"])  # Reemplaza con: list[GroupRead]
async def read_all(session: AsyncSession = Depends(get_session)):
    return await get_all_groups(session)

@router.get("/{group_id}", response_model="GroupRead")  # Reemplaza con: response_model=GroupRead
async def read(group_id: UUID, session: AsyncSession = Depends(get_session)):
    group = await get_group(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group

@router.put("/{group_id}", response_model="GroupRead")  # Reemplaza con: response_model=GroupRead
async def update(group_id: UUID, data: "GroupUpdate", session: AsyncSession = Depends(get_session)):  # Reemplaza con: data: GroupUpdate
    group = await update_group(session, group_id, data)
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group

@router.delete("/{group_id}")
async def delete(group_id: UUID, session: AsyncSession = Depends(get_session)):
    success = await delete_group(session, group_id)
    if not success:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return {"ok": True}
