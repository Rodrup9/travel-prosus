from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group

class IAChat(Base):
    __tablename__ = "ia_chat"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"))
    
    message: Mapped[str] = mapped_column(String)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="ia_chats")
    group = relationship("Group", back_populates="ia_chats")
