from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from app.database import async_session

# TODO: Crear modelo GroupMember en app/models/group_member.py
# Estructura sugerida:
# class GroupMember(SQLModel, table=True):
#     group_id: UUID = Field(foreign_key="group.id", primary_key=True)
#     user_id: UUID = Field(foreign_key="user.id", primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     status: bool = True

# TODO: Crear esquemas en app/schemas/group_member.py
# from app.schemas.group_member import GroupMemberCreate, GroupMemberRead, GroupMemberUpdate

# TODO: Crear servicios en app/services/group_member.py
# from app.services.group_member import (
#     create_group_member,
#     get_group_member,
#     get_all_group_members,
#     get_group_members_by_group,
#     get_group_members_by_user,
#     update_group_member,
#     delete_group_member,
# )

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/")  # TODO: Agregar response_model=GroupMemberRead
async def create(data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por GroupMemberCreate
    """
    Crear un nuevo miembro de grupo.
    Requiere: group_id, user_id
    """
    # TODO: return await create_group_member(session, data)
    raise HTTPException(status_code=501, detail="Implementar create_group_member service")

@router.get("/")  # TODO: Agregar response_model=list[GroupMemberRead]
async def read_all(session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los miembros de grupos.
    """
    # TODO: return await get_all_group_members(session)
    raise HTTPException(status_code=501, detail="Implementar get_all_group_members service")

@router.get("/group/{group_id}")  # TODO: Agregar response_model=list[GroupMemberRead]
async def read_by_group(group_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los miembros de un grupo específico.
    """
    # TODO: return await get_group_members_by_group(session, group_id)
    raise HTTPException(status_code=501, detail="Implementar get_group_members_by_group service")

@router.get("/user/{user_id}")  # TODO: Agregar response_model=list[GroupMemberRead]
async def read_by_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los grupos de un usuario específico.
    """
    # TODO: return await get_group_members_by_user(session, user_id)
    raise HTTPException(status_code=501, detail="Implementar get_group_members_by_user service")

@router.get("/{group_id}/{user_id}")  # TODO: Agregar response_model=GroupMemberRead
async def read(group_id: UUID, user_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener un miembro específico de un grupo.
    """
    # TODO: Implementar get_group_member service
    # group_member = await get_group_member(session, group_id, user_id)
    # if not group_member:
    #     raise HTTPException(status_code=404, detail="Miembro del grupo no encontrado")
    # return group_member
    raise HTTPException(status_code=501, detail="Implementar get_group_member service")

@router.put("/{group_id}/{user_id}")  # TODO: Agregar response_model=GroupMemberRead
async def update(group_id: UUID, user_id: UUID, data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por GroupMemberUpdate
    """
    Actualizar un miembro de grupo (normalmente solo el status).
    """
    # TODO: Implementar update_group_member service
    # group_member = await update_group_member(session, group_id, user_id, data)
    # if not group_member:
    #     raise HTTPException(status_code=404, detail="Miembro del grupo no encontrado")
    # return group_member
    raise HTTPException(status_code=501, detail="Implementar update_group_member service")

@router.delete("/{group_id}/{user_id}")
async def delete(group_id: UUID, user_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Eliminar un miembro de un grupo.
    """
    # TODO: Implementar delete_group_member service
    # success = await delete_group_member(session, group_id, user_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Miembro del grupo no encontrado")
    # return {"ok": True}
    raise HTTPException(status_code=501, detail="Implementar delete_group_member service")