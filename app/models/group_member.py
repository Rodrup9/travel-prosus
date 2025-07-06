from sqlalchemy import Boolean, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="members")