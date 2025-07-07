from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group

class IAChat(Base):
    __tablename__ = "ia_chat"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("groups.id"))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relaciones
    user = relationship("User", back_populates="ia_chats")
    group = relationship("Group", back_populates="ia_chats")
