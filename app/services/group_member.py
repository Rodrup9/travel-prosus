from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.group_member import GroupMember
from app.models.group import Group
from app.schemas.group_member import GroupMemberCreate, GroupMemberUpdate
from typing import Optional, List
import uuid

class GroupMemberService:

    @staticmethod
    async def create_member(db: AsyncSession, member: GroupMemberCreate) -> GroupMember:
        db_member = GroupMember(
            group_id=member.group_id,
            user_id=member.user_id,
            status=member.status
        )
        try:
            db.add(db_member)
            await db.commit()
            await db.refresh(db_member)
            return db_member
        except IntegrityError:
            await db.rollback()
            raise ValueError("Ya existe este miembro en el grupo o claves inválidas")

    @staticmethod
    async def get_member_by_ids(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID) -> Optional[GroupMember]:
        result = await db.execute(select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_members(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[GroupMember]:
        result = await db.execute(select(GroupMember).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_members_by_user(db: AsyncSession, user_id: uuid.UUID) -> List[GroupMember]:
        # Hacer join con la tabla Group para obtener el nombre del grupo
        stmt = select(GroupMember, Group.name.label('group_name')).join(
            Group, GroupMember.group_id == Group.id
        ).filter(GroupMember.user_id == user_id)
        
        result = await db.execute(stmt)
        members_data = result.all()
        
        # Crear objetos GroupMember con el nombre del grupo
        result_list = []
        for member, group_name in members_data:
            member.name = group_name
            result_list.append(member)
        
        return result_list

    @staticmethod
    async def update_member(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID, member_update: GroupMemberUpdate) -> Optional[GroupMember]:
        result = await db.execute(select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ))
        db_member = result.scalar_one_or_none()
        if not db_member:
            return None

        update_data = member_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_member, field, value)

        try:
            await db.commit()
            await db.refresh(db_member)
            return db_member
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error al actualizar miembro del grupo")

    @staticmethod
    async def delete_member(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        result = await db.execute(select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ))
        db_member = result.scalar_one_or_none()
        if not db_member:
            return False

        await db.delete(db_member)
        await db.commit()
        return True

    @staticmethod
    async def toggle_member_status(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID) -> Optional[GroupMember]:
        result = await db.execute(select(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ))
        db_member = result.scalar_one_or_none()
        if not db_member:
            return None

        db_member.status = not db_member.status
        await db.commit()
        await db.refresh(db_member)
        return db_member