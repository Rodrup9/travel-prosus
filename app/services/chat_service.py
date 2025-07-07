from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from app.models.ia_chat import IAChat
from app.models.user import User
from app.models.group import Group

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def save_message(self, user_id: uuid.UUID, group_id: uuid.UUID, message: str) -> IAChat:
        """
        Guarda un mensaje en el historial de chat
        """
        chat_message = IAChat(
            user_id=user_id,
            group_id=group_id,
            message=message
        )
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message

    def get_chat_history(
        self, 
        group_id: uuid.UUID, 
        limit: int = 50,
        hours: Optional[int] = None
    ) -> List[IAChat]:
        """
        Obtiene el historial de chat de un grupo
        
        Args:
            group_id: ID del grupo
            limit: Número máximo de mensajes a retornar
            hours: Si se especifica, solo retorna mensajes de las últimas X horas
        """
        query = self.db.query(IAChat)\
            .filter(IAChat.group_id == group_id)\
            .filter(IAChat.status == True)\
            .order_by(IAChat.created_at.desc())

        if hours:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(IAChat.created_at >= time_threshold)

        return query.limit(limit).all()

    def get_user_context(self, user_id: uuid.UUID) -> dict:
        """
        Obtiene el contexto del usuario basado en su historial
        """
        # Obtener el usuario y sus datos básicos
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}

        # Obtener los últimos mensajes del usuario
        recent_messages = self.db.query(IAChat)\
            .filter(IAChat.user_id == user_id)\
            .filter(IAChat.status == True)\
            .order_by(IAChat.created_at.desc())\
            .limit(10)\
            .all()

        # Construir el contexto
        context = {
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email
            },
            "recent_interactions": [
                {
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat(),
                    "group_id": str(msg.group_id)
                }
                for msg in recent_messages
            ]
        }

        return context

    def get_group_context(self, group_id: uuid.UUID) -> dict:
        """
        Obtiene el contexto del grupo basado en su historial
        """
        # Obtener el grupo y sus miembros
        group = self.db.query(Group).filter(Group.id == group_id).first()
        if not group:
            return {}

        # Obtener los últimos mensajes del grupo
        recent_messages = self.get_chat_history(group_id, limit=15)

        # Construir el contexto
        context = {
            "group": {
                "id": str(group.id),
                "name": group.name,
                "host_id": str(group.host_id)
            },
            "recent_messages": [
                {
                    "user_id": str(msg.user_id),
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in recent_messages
            ]
        }

        return context

    def delete_message(self, message_id: uuid.UUID) -> bool:
        """
        Elimina lógicamente un mensaje del historial
        """
        message = self.db.query(IAChat).filter(IAChat.id == message_id).first()
        if not message:
            return False

        message.status = False
        self.db.commit()
        return True 