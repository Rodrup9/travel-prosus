from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from app.models.ia_chat import IAChat
from app.models.user import User
from app.models.group import Group

class ChatServiceSync:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_message(self, user_id: uuid.UUID, group_id: uuid.UUID, message: str) -> IAChat:
        """
        Guarda un mensaje en el historial de chat
        """
        chat_message = IAChat(
            user_id=user_id,
            group_id=group_id,
            message=message
        )
        self.db.add(chat_message)
        await self.db.commit()
        await self.db.refresh(chat_message)
        return chat_message

    async def get_chat_history(
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
        stmt = select(IAChat).where(
            IAChat.group_id == group_id,
            IAChat.status == True
        ).order_by(IAChat.created_at.desc())

        if hours:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            stmt = stmt.where(IAChat.created_at >= time_threshold)

        stmt = stmt.limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_context(self, user_id: uuid.UUID) -> dict:
        """
        Obtiene el contexto del usuario basado en su historial
        """
        # Obtener el usuario y sus datos básicos
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return {}

        # Obtener los últimos mensajes del usuario
        stmt = select(IAChat).where(
            IAChat.user_id == user_id,
            IAChat.status == True
        ).order_by(IAChat.created_at.desc()).limit(10)
        result = await self.db.execute(stmt)
        recent_messages = list(result.scalars().all())

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

    async def get_group_context(self, group_id: uuid.UUID) -> dict:
        """
        Obtiene el contexto del grupo basado en su historial
        """
        # Obtener el grupo y sus miembros
        stmt = select(Group).where(Group.id == group_id)
        result = await self.db.execute(stmt)
        group = result.scalar_one_or_none()
        
        if not group:
            return {}

        # Obtener los últimos mensajes del grupo
        recent_messages = await self.get_chat_history(group_id, limit=15)

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

    async def delete_message(self, message_id: uuid.UUID) -> bool:
        """
        Elimina lógicamente un mensaje del historial
        """
        stmt = select(IAChat).where(IAChat.id == message_id)
        result = await self.db.execute(stmt)
        message = result.scalar_one_or_none()
        
        if not message:
            return False

        message.status = False
        await self.db.commit()
        return True 