from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.user import Users
from app.schemas.user import UserCreate, UserUpdate
from uuid import UUID

async def create_user(session: AsyncSession, data: UserCreate) -> Users:
    user = Users(**data.dict())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def get_user(session: AsyncSession, user_id: UUID) -> Users | None:
    result = await session.execute(select(Users).where(Users.id == user_id))
    return result.scalar_one_or_none()

async def get_all_users(session: AsyncSession) -> list[Users]:
    result = await session.execute(select(Users))
    return result.scalars().all()

async def update_user(session: AsyncSession, user_id: UUID, data: UserUpdate) -> Users | None:
    user = await get_user(session, user_id)
    if not user:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def delete_user(session: AsyncSession, user_id: UUID) -> bool:
    user = await get_user(session, user_id)
    if not user:
        return False
    await session.delete(user)
    await session.commit()
    return True
