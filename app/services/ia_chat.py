from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.ia_chat import IAChat
from app.models.user import User
from app.models.group import Group
from app.schemas.ia_chat import IAChatCreate, IAChatUpdate
from typing import Optional, List
import uuid

class IAChatService:

    @staticmethod
    async def create_message(db: AsyncSession, chat_data: IAChatCreate) -> IAChat:
        db_chat = IAChat(
            id=uuid.uuid4(),
            user_id=chat_data.user_id,
            group_id=chat_data.group_id,
            message=chat_data.message,
            status=chat_data.status
        )
        try:
            db.add(db_chat)
            await db.commit()
            await db.refresh(db_chat)
            return db_chat
        except IntegrityError as e:
            await db.rollback()
            raise ValueError("Error al crear mensaje: " + str(e.orig))

    @staticmethod
    async def get_message_by_id(db: AsyncSession, message_id: uuid.UUID) -> Optional[IAChat]:
        result = await db.execute(select(IAChat).filter(IAChat.id == message_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_messages(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[IAChat]:
        result = await db.execute(select(IAChat).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_message(db: AsyncSession, message_id: uuid.UUID, chat_update: IAChatUpdate) -> Optional[IAChat]:
        result = await db.execute(select(IAChat).filter(IAChat.id == message_id))
        db_chat = result.scalar_one_or_none()
        if not db_chat:
            return None

        update_data = chat_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chat, field, value)

        try:
            await db.commit()
            await db.refresh(db_chat)
            return db_chat
        except IntegrityError:
            await db.rollback()
            raise ValueError("Error al actualizar mensaje")

    @staticmethod
    async def delete_message(db: AsyncSession, message_id: uuid.UUID) -> bool:
        result = await db.execute(select(IAChat).filter(IAChat.id == message_id))
        db_chat = result.scalar_one_or_none()
        if not db_chat:
            return False

        await db.delete(db_chat)
        await db.commit()
        return True

    @staticmethod
    async def toggle_status(db: AsyncSession, message_id: uuid.UUID) -> Optional[IAChat]:
        result = await db.execute(select(IAChat).filter(IAChat.id == message_id))
        db_chat = result.scalar_one_or_none()
        if not db_chat:
            return None

        db_chat.status = not db_chat.status
        await db.commit()
        await db.refresh(db_chat)
        return db_chat

    @staticmethod
    async def get_messages_by_user(db: AsyncSession, user_id: uuid.UUID) -> List[IAChat]:
        result = await db.execute(select(IAChat).filter(IAChat.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def get_messages_by_group(db: AsyncSession, group_id: uuid.UUID) -> List[IAChat]:
        result = await db.execute(select(IAChat).filter(IAChat.group_id == group_id))
        return result.scalars().all()

    @staticmethod
    async def get_messages_by_user_and_group(db: AsyncSession, user_id: uuid.UUID, group_id: uuid.UUID) -> List[IAChat]:
        result = await db.execute(select(IAChat).filter(
            IAChat.user_id == user_id,
            IAChat.group_id == group_id
        ))
        return result.scalars().all()
