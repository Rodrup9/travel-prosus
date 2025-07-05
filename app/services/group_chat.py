from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.group_chat import GroupChat
from app.schemas.group_chat import GroupChatCreate, GroupChatUpdate
from uuid import UUID

async def create_group_chat(session: AsyncSession, data: GroupChatCreate) -> GroupChat:
    group_chat = GroupChat(**data.dict())
    session.add(group_chat)
    await session.commit()
    await session.refresh(group_chat)
    return group_chat

async def get_group_chat(session: AsyncSession, chat_id: UUID) -> GroupChat | None:
    result = await session.execute(select(GroupChat).where(GroupChat.id == chat_id))
    return result.scalar_one_or_none()

async def get_all_group_chats(session: AsyncSession) -> list[GroupChat]:
    result = await session.execute(select(GroupChat))
    return result.scalars().all()

async def get_group_chats_by_group(session: AsyncSession, group_id: UUID) -> list[GroupChat]:
    result = await session.execute(select(GroupChat).where(GroupChat.group_id == group_id))
    return result.scalars().all()

async def get_group_chats_by_user(session: AsyncSession, user_id: UUID) -> list[GroupChat]:
    result = await session.execute(select(GroupChat).where(GroupChat.user_id == user_id))
    return result.scalars().all()

async def update_group_chat(session: AsyncSession, chat_id: UUID, data: GroupChatUpdate) -> GroupChat | None:
    group_chat = await get_group_chat(session, chat_id)
    if not group_chat:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(group_chat, key, value)
    session.add(group_chat)
    await session.commit()
    await session.refresh(group_chat)
    return group_chat

async def delete_group_chat(session: AsyncSession, chat_id: UUID) -> bool:
    group_chat = await get_group_chat(session, chat_id)
    if not group_chat:
        return False
    await session.delete(group_chat)
    await session.commit()
    return True
