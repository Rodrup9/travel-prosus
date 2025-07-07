from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User    
from app.models.group_member import GroupMember
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List
import uuid
from app.supabaseClient import get_supabase_client

class UserService:
    
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """Crear un nuevo usuario"""
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        print(response)
        if not response.user:
            raise ValueError("Error al crear el usuario")
        
        db_user = User(
            id=response.user.id,
            name=user.name,
            email=user.email,
            status=user.status,
            avatar_url=user.avatar_url
        )
        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("El email ya está registrado")
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Obtener usuario por ID"""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_group_id(db: AsyncSession, group_id: uuid.UUID) -> List[User]:
        result = await db.execute(
            select(User).join(GroupMember, User.id == GroupMember.user_id)
            .filter(GroupMember.group_id == group_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener lista de usuarios"""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
        """Actualizar usuario"""
        result = await db.execute(select(User).filter(User.id == user_id))
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("El email ya está registrado")
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
        """Eliminar usuario"""
        result = await db.execute(select(User).filter(User.id == user_id))
        db_user = result.scalar_one_or_none()
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True
    
    @staticmethod
    async def toggle_user_status(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Cambiar el estado del usuario"""
        result = await db.execute(select(User).filter(User.id == user_id))
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
        
        db_user.status = not db_user.status
        await db.commit()
        await db.refresh(db_user)
        return db_user