from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.group_member import GroupMember
from app.schemas.group_member import GroupMemberCreate, GroupMemberUpdate
from uuid import UUID

async def create_group_member(session: AsyncSession, data: GroupMemberCreate) -> GroupMember:
    group_member = GroupMember(**data.dict())
    session.add(group_member)
    await session.commit()
    await session.refresh(group_member)
    return group_member

async def get_group_member(session: AsyncSession, group_id: UUID, user_id: UUID) -> GroupMember | None:
    result = await session.execute(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def get_all_group_members(session: AsyncSession) -> list[GroupMember]:
    result = await session.execute(select(GroupMember))
    return result.scalars().all()

async def get_group_members_by_group(session: AsyncSession, group_id: UUID) -> list[GroupMember]:
    result = await session.execute(select(GroupMember).where(GroupMember.group_id == group_id))
    return result.scalars().all()

async def get_group_members_by_user(session: AsyncSession, user_id: UUID) -> list[GroupMember]:
    result = await session.execute(select(GroupMember).where(GroupMember.user_id == user_id))
    return result.scalars().all()

async def update_group_member(session: AsyncSession, group_id: UUID, user_id: UUID, data: GroupMemberUpdate) -> GroupMember | None:
    group_member = await get_group_member(session, group_id, user_id)
    if not group_member:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(group_member, key, value)
    session.add(group_member)
    await session.commit()
    await session.refresh(group_member)
    return group_member

async def delete_group_member(session: AsyncSession, group_id: UUID, user_id: UUID) -> bool:
    group_member = await get_group_member(session, group_id, user_id)
    if not group_member:
        return False
    await session.delete(group_member)
    await session.commit()
    return True
