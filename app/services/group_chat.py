from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.group_chat import GroupChat
from app.schemas.group_chat import GroupChatCreate, GroupChatUpdate
from typing import Optional, List
import uuid

class GroupChatService:

    @staticmethod
    async def create_group_chat(db: AsyncSession, chat: GroupChatCreate) -> GroupChat:
        db_chat = GroupChat(
            id=uuid.uuid4(),
            user_id=chat.user_id,
            group_id=chat.group_id,
            message=chat.message,
            status=chat.status
        )
        try:
            db.add(db_chat)
            await db.commit()
            await db.refresh(db_chat)
            return db_chat
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Error al crear el mensaje: {str(e.orig)}")

    @staticmethod
    async def get_group_chat_by_id(db: AsyncSession, message_id: uuid.UUID) -> Optional[GroupChat]:
        result = await db.execute(select(GroupChat).filter(GroupChat.id == message_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_group_chats(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[GroupChat]:
        result = await db.execute(select(GroupChat).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_group_chats_by_group(db: AsyncSession, group_id: uuid.UUID) -> List[GroupChat]:
        result = await db.execute(select(GroupChat).filter(GroupChat.group_id == group_id).order_by(GroupChat.created_at))
        return result.scalars().all()

    @staticmethod
    async def get_user_messages_in_group(db: AsyncSession, group_id: uuid.UUID, user_id: uuid.UUID) -> List[GroupChat]:
        result = await db.execute(select(GroupChat).filter(
            GroupChat.group_id == group_id,
            GroupChat.user_id == user_id
        ).order_by(GroupChat.created_at))
        return result.scalars().all()

    @staticmethod
    async def update_group_chat(db: AsyncSession, message_id: uuid.UUID, chat_update: GroupChatUpdate) -> Optional[GroupChat]:
        result = await db.execute(select(GroupChat).filter(GroupChat.id == message_id))
        db_chat = result.scalar_one_or_none()
        if not db_chat:
            return None

        update_data = chat_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chat, field, value)

        await db.commit()
        await db.refresh(db_chat)
        return db_chat

    @staticmethod
    async def delete_group_chat(db: AsyncSession, message_id: uuid.UUID) -> bool:
        result = await db.execute(select(GroupChat).filter(GroupChat.id == message_id))
        db_chat = result.scalar_one_or_none()
        if not db_chat:
            return False

        await db.delete(db_chat)
        await db.commit()
        return True

    @staticmethod
    async def toggle_status(db: AsyncSession, message_id: uuid.UUID) -> Optional[GroupChat]:
        result = await db.execute(select(GroupChat).filter(GroupChat.id == message_id))
        db_chat = result.scalar_one_or_none()
        if not db_chat:
            return None

        db_chat.status = not db_chat.status
        await db.commit()
        await db.refresh(db_chat)
        return db_chat
