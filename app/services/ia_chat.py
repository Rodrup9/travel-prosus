from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.ia_chat import IAChat
from app.models.user import User
from app.models.group import Group
from app.schemas.ia_chat import IAChatCreate, IAChatUpdate
from typing import Optional, List
import uuid

class IAChatService:

    @staticmethod
    def create_message(db: Session, chat_data: IAChatCreate) -> IAChat:
        db_chat = IAChat(
            id=uuid.uuid4(),
            user_id=chat_data.user_id,
            group_id=chat_data.group_id,
            message=chat_data.message,
            status=chat_data.status
        )
        try:
            db.add(db_chat)
            db.commit()
            db.refresh(db_chat)
            return db_chat
        except IntegrityError as e:
            db.rollback()
            raise ValueError("Error al crear mensaje: " + str(e.orig))

    @staticmethod
    def get_message_by_id(db: Session, message_id: uuid.UUID) -> Optional[IAChat]:
        return db.query(IAChat).filter(IAChat.id == message_id).first()

    @staticmethod
    def get_all_messages(db: Session, skip: int = 0, limit: int = 100) -> List[IAChat]:
        return db.query(IAChat).offset(skip).limit(limit).all()

    @staticmethod
    def update_message(db: Session, message_id: uuid.UUID, chat_update: IAChatUpdate) -> Optional[IAChat]:
        db_chat = db.query(IAChat).filter(IAChat.id == message_id).first()
        if not db_chat:
            return None

        update_data = chat_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chat, field, value)

        try:
            db.commit()
            db.refresh(db_chat)
            return db_chat
        except IntegrityError:
            db.rollback()
            raise ValueError("Error al actualizar mensaje")

    @staticmethod
    def delete_message(db: Session, message_id: uuid.UUID) -> bool:
        db_chat = db.query(IAChat).filter(IAChat.id == message_id).first()
        if not db_chat:
            return False

        db.delete(db_chat)
        db.commit()
        return True

    @staticmethod
    def toggle_status(db: Session, message_id: uuid.UUID) -> Optional[IAChat]:
        db_chat = db.query(IAChat).filter(IAChat.id == message_id).first()
        if not db_chat:
            return None

        db_chat.status = not db_chat.status
        db.commit()
        db.refresh(db_chat)
        return db_chat

    @staticmethod
    def get_messages_by_user(db: Session, user_id: uuid.UUID) -> List[IAChat]:
        return db.query(IAChat).filter(IAChat.user_id == user_id).all()

    @staticmethod
    def get_messages_by_group(db: Session, group_id: uuid.UUID) -> List[IAChat]:
        return db.query(IAChat).filter(IAChat.group_id == group_id).all()

    @staticmethod
    def get_messages_by_user_and_group(db: Session, user_id: uuid.UUID, group_id: uuid.UUID) -> List[IAChat]:
        return db.query(IAChat).filter(
            IAChat.user_id == user_id,
            IAChat.group_id == group_id
        ).all()
