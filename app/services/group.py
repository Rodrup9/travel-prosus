from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate
from uuid import UUID

async def create_group(session: AsyncSession, data: GroupCreate) -> Group:
    group = Group(**data.dict())
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group

async def get_group(session: AsyncSession, group_id: UUID) -> Group | None:
    result = await session.execute(select(Group).where(Group.id == group_id))
    return result.scalar_one_or_none()

async def get_all_groups(session: AsyncSession) -> list[Group]:
    result = await session.execute(select(Group))
    return result.scalars().all()

async def update_group(session: AsyncSession, group_id: UUID, data: GroupUpdate) -> Group | None:
    group = await get_group(session, group_id)
    if not group:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(group, key, value)
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group

async def delete_group(session: AsyncSession, group_id: UUID) -> bool:
    group = await get_group(session, group_id)
    if not group:
        return False
    await session.delete(group)
    await session.commit()
    return True
