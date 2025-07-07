from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.group_chat import GroupChat
from app.schemas.group_chat import GroupChatCreate, GroupChatUpdate
from typing import Optional, List
import uuid

class GroupChatService:

    @staticmethod
    def create_message(db: Session, chat: GroupChatCreate) -> GroupChat:
        db_chat = GroupChat(
            id=uuid.uuid4(),
            user_id=chat.user_id,
            group_id=chat.group_id,
            message=chat.message,
            status=chat.status
        )
        try:
            db.add(db_chat)
            db.commit()
            db.refresh(db_chat)
            return db_chat
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al crear el mensaje: {str(e.orig)}")

    @staticmethod
    def get_message_by_id(db: Session, message_id: uuid.UUID) -> Optional[GroupChat]:
        return db.query(GroupChat).filter(GroupChat.id == message_id).first()

    @staticmethod
    def get_all_messages(db: Session, skip: int = 0, limit: int = 100) -> List[GroupChat]:
        return db.query(GroupChat).offset(skip).limit(limit).all()

    @staticmethod
    def get_messages_by_group(db: Session, group_id: uuid.UUID) -> List[GroupChat]:
        return db.query(GroupChat).filter(GroupChat.group_id == group_id).order_by(GroupChat.created_at).all()

    @staticmethod
    def get_user_messages_in_group(db: Session, group_id: uuid.UUID, user_id: uuid.UUID) -> List[GroupChat]:
        return db.query(GroupChat).filter(
            GroupChat.group_id == group_id,
            GroupChat.user_id == user_id
        ).order_by(GroupChat.created_at).all()

    @staticmethod
    def update_message(db: Session, message_id: uuid.UUID, chat_update: GroupChatUpdate) -> Optional[GroupChat]:
        db_chat = db.query(GroupChat).filter(GroupChat.id == message_id).first()
        if not db_chat:
            return None

        update_data = chat_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chat, field, value)

        db.commit()
        db.refresh(db_chat)
        return db_chat

    @staticmethod
    def delete_message(db: Session, message_id: uuid.UUID) -> bool:
        db_chat = db.query(GroupChat).filter(GroupChat.id == message_id).first()
        if not db_chat:
            return False

        db.delete(db_chat)
        db.commit()
        return True

    @staticmethod
    def toggle_status(db: Session, message_id: uuid.UUID) -> Optional[GroupChat]:
        db_chat = db.query(GroupChat).filter(GroupChat.id == message_id).first()
        if not db_chat:
            return None

        db_chat.status = not db_chat.status
        db.commit()
        db.refresh(db_chat)
        return db_chat
