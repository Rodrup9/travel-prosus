from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.group import Group
from app.services.group_member import GroupMemberService
from app.models.user import User
from app.schemas.group_member import GroupMemberCreate
from app.schemas.group import GroupCreate, GroupUpdate
from typing import Optional, List
import uuid

class GroupService:
    
    @staticmethod
    async def create_group(db: AsyncSession, group: GroupCreate) -> Group:
        result = await db.execute(select(User).filter(User.id == group.host_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("El host_id no existe en la tabla users")
        
        db_group = Group(
            id=uuid.uuid4(),
            name=group.name,
            host_id=group.host_id,
            status=group.status,
        )
        try:
            db.add(db_group)
            await db.commit()
            await db.refresh(db_group)
            await GroupMemberService.create_member(db, GroupMemberCreate(
                group_id=db_group.id,
                user_id=group.host_id,
                status=True
            ))
            return db_group
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear Grupo: {str(e.orig)}")

    
    @staticmethod
    async def get_group_by_id(db: AsyncSession, group_id: uuid.UUID) -> Optional[Group]:
        result = await db.execute(select(Group).filter(Group.id == group_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, group_id: uuid.UUID) -> Optional[Group]:
        result = await db.execute(select(Group).filter(Group.id == group_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_groups(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Group]:
        result = await db.execute(select(Group).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: uuid.UUID) -> List[Group]:
        result = await db.execute(select(Group).filter(Group.host_id == user_id))
        return result.scalars().all()
    
    @staticmethod
    async def update_group(db: AsyncSession, group_id: uuid.UUID, group_update: GroupUpdate) -> Optional[Group]:
        result = await db.execute(select(Group).filter(Group.id == group_id))
        db_group = result.scalar_one_or_none()
        if not db_group:
            return None
        
        update_data = group_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_group, field, value)
        
        try:
            await db.commit()
            await db.refresh(db_group)
            return db_group
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error al actualizar ")
    
    @staticmethod
    async def delete_group(db: AsyncSession, group_id: uuid.UUID) -> bool:
        result = await db.execute(select(Group).filter(Group.id == group_id))
        db_group = result.scalar_one_or_none()
        if not db_group:
            return False
        
        await db.delete(db_group)
        await db.commit()
        return True
    
    @staticmethod
    async def toggle_group_status(db: AsyncSession, group_id: uuid.UUID) -> Optional[Group]:
        result = await db.execute(select(Group).filter(Group.id == group_id))
        db_group = result.scalar_one_or_none()
        if not db_group:
            return None
        
        db_group.status = not db_group.status
        await db.commit()
        await db.refresh(db_group)
        return db_group
    
    @staticmethod
    async def get_groups_by_host_id(db: AsyncSession, host_id: uuid.UUID) -> List[Group]:
        result = await db.execute(select(Group).filter(Group.host_id == host_id))
        return result.scalars().all()