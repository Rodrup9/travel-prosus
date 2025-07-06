from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.ia_chat import IaChat
from app.schemas.ia_chat import IaChatCreate, IaChatUpdate
from uuid import UUID

async def create_ia_chat(session: AsyncSession, data: IaChatCreate) -> IaChat:
    ia_chat = IaChat(**data.dict())
    session.add(ia_chat)
    await session.commit()
    await session.refresh(ia_chat)
    return ia_chat

async def get_ia_chat(session: AsyncSession, chat_id: UUID) -> IaChat | None:
    result = await session.execute(select(IaChat).where(IaChat.id == chat_id))
    return result.scalar_one_or_none()

async def get_all_ia_chats(session: AsyncSession) -> list[IaChat]:
    result = await session.execute(select(IaChat))
    return result.scalars().all()

async def get_ia_chats_by_group(session: AsyncSession, group_id: UUID) -> list[IaChat]:
    result = await session.execute(select(IaChat).where(IaChat.group_id == group_id))
    return result.scalars().all()

async def get_ia_chats_by_user(session: AsyncSession, user_id: UUID) -> list[IaChat]:
    result = await session.execute(select(IaChat).where(IaChat.user_id == user_id))
    return result.scalars().all()

async def update_ia_chat(session: AsyncSession, chat_id: UUID, data: IaChatUpdate) -> IaChat | None:
    ia_chat = await get_ia_chat(session, chat_id)
    if not ia_chat:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(ia_chat, key, value)
    session.add(ia_chat)
    await session.commit()
    await session.refresh(ia_chat)
    return ia_chat

async def delete_ia_chat(session: AsyncSession, chat_id: UUID) -> bool:
    ia_chat = await get_ia_chat(session, chat_id)
    if not ia_chat:
        return False
    await session.delete(ia_chat)
    await session.commit()
    return True
