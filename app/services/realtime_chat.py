import asyncio
import json
import uuid
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from app.services.group_chat import GroupChatService
from app.schemas.group_chat import GroupChatCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, get_sync_db
from app.models.user import User
from sqlalchemy import select

class RealtimeChatManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, group_id: str):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = set()
        self.active_connections[group_id].add(websocket)
        
        # Enviar mensajes anteriores al conectar
        await self._send_previous_messages(websocket, group_id)
        
        print(f"Usuario conectado al grupo {group_id}. Conexiones activas: {len(self.active_connections[group_id])}")
        
    def disconnect(self, websocket: WebSocket, group_id: str):
        if group_id in self.active_connections:
            self.active_connections[group_id].discard(websocket)
            if not self.active_connections[group_id]:
                del self.active_connections[group_id]
        print(f"Usuario desconectado del grupo {group_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_group(self, message: str, group_id: str, exclude_websocket: Optional[WebSocket] = None):
        if group_id in self.active_connections:
            for connection in self.active_connections[group_id]:
                if connection != exclude_websocket:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        print(f"Error enviando mensaje: {e}")
                        # Si hay error, remover la conexión
                        self.active_connections[group_id].discard(connection)
    
    async def _send_previous_messages(self, websocket: WebSocket, group_id: str):
        """Enviar mensajes anteriores al conectar"""
        try:
            # Usar sesión asíncrona
            async for db in get_db():
                messages = await GroupChatService.get_group_chats_by_group(db, uuid.UUID(group_id))
                
                # Obtener información de usuarios para los mensajes
                user_ids = [msg.user_id for msg in messages]
                if user_ids:
                    # Consulta asíncrona para obtener usuarios
                    stmt = select(User).where(User.id.in_(user_ids))
                    result = await db.execute(stmt)
                    users = result.scalars().all()
                    user_dict = {user.id: user.name for user in users}
                else:
                    user_dict = {}
                
                # Enviar mensaje de historial
                history_message = {
                    "type": "message_history",
                    "data": [
                        {
                            "id": str(msg.id),
                            "user_id": str(msg.user_id),
                            "group_id": str(msg.group_id),
                            "message": msg.message,
                            "created_at": str(msg.created_at),
                            "status": msg.status,
                            "user_name": user_dict.get(msg.user_id, "Usuario desconocido")
                        }
                        for msg in messages
                    ]
                }
                
                await websocket.send_text(json.dumps(history_message))
                print(f"Enviados {len(messages)} mensajes anteriores al grupo {group_id}")
                break  # Salir del generador asíncrono
                
        except Exception as e:
            print(f"Error enviando mensajes anteriores: {e}")
    
    async def broadcast_new_message(self, message_data: dict, group_id: str):
        """Broadcast de un nuevo mensaje a todos los clientes del grupo"""
        message = {
            "type": "new_message",
            "data": message_data
        }
        
        await self.broadcast_to_group(json.dumps(message), group_id)
        print(f"Mensaje broadcast enviado al grupo {group_id}")

# Instancia global del manager
realtime_manager = RealtimeChatManager() 