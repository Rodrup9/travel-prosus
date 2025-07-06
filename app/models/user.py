from sqlalchemy import Column, Integer, String, DateTime, Uuid, Boolean
from sqlalchemy.sql import func
from app.database import Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from app.models.group import Group

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    # groups: Mapped[list["Group"]] = relationship("Group", back_populates="host")
    groups = relationship("Group", back_populates="host", cascade="all, delete")
    group_memberships = relationship("GroupMember", back_populates="user")
    group_chats = relationship("GroupChat", back_populates="user")
    ia_chats = relationship("IAChat", back_populates="user")
    votes = relationship("Vote", back_populates="user")
