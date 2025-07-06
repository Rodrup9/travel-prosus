from sqlalchemy import Integer, String, DateTime, Uuid, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column , relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from typing import TYPE_CHECKING

from app.models.trip import Trip
if TYPE_CHECKING:
    from app.models.user import User


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    # host_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    host_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id")
    )
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    host = relationship("User", back_populates="groups")
    members = relationship("GroupMember", back_populates="group")
    chats = relationship("GroupChat", back_populates="group")
    ia_chats = relationship("IaChat", back_populates="group")
    trips = relationship("Trip", back_populates="group")
