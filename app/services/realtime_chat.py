import asyncio
import json
import uuid
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from supabase import Client
from app.supabaseClient import get_supabase_client
from app.services.group_chat import GroupChatService
from app.schemas.group_chat import GroupChatCreate
from sqlalchemy.orm import Session
from app.database import get_db

class RealtimeChatManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.supabase: Client = get_supabase_client()
        
    async def connect(self, websocket: WebSocket, group_id: str):
        await websocket.accept()
        if group_id not in self.active_connections:
            self.active_connections[group_id] = set()
        self.active_connections[group_id].add(websocket)
        
        # Suscribirse a cambios en Supabase para este grupo
        await self._subscribe_to_supabase_changes(group_id)
        
    def disconnect(self, websocket: WebSocket, group_id: str):
        if group_id in self.active_connections:
            self.active_connections[group_id].discard(websocket)
            if not self.active_connections[group_id]:
                del self.active_connections[group_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_group(self, message: str, group_id: str, exclude_websocket: Optional[WebSocket] = None):
        if group_id in self.active_connections:
            for connection in self.active_connections[group_id]:
                if connection != exclude_websocket:
                    try:
                        await connection.send_text(message)
                    except:
                        # Si hay error, remover la conexión
                        self.active_connections[group_id].discard(connection)
    
    async def _subscribe_to_supabase_changes(self, group_id: str):
        """Suscribirse a cambios en la tabla group_chat de Supabase"""
        try:
            # Crear suscripción a cambios en la tabla group_chat
            subscription = self.supabase.table('group_chat').on(
                'INSERT',
                filter=f'group_id=eq.{group_id}'
            ).subscribe(self._handle_supabase_message)
            
            # También suscribirse a actualizaciones
            subscription_update = self.supabase.table('group_chat').on(
                'UPDATE',
                filter=f'group_id=eq.{group_id}'
            ).subscribe(self._handle_supabase_update)
            
        except Exception as e:
            print(f"Error al suscribirse a Supabase: {e}")
    
    def _handle_supabase_message(self, payload):
        """Manejar nuevos mensajes desde Supabase"""
        try:
            message_data = payload['record']
            group_id = str(message_data['group_id'])
            
            # Crear mensaje para broadcast
            message = {
                "type": "new_message",
                "data": {
                    "id": str(message_data['id']),
                    "user_id": str(message_data['user_id']),
                    "group_id": str(message_data['group_id']),
                    "message": message_data['message'],
                    "created_at": message_data['created_at'],
                    "status": message_data['status']
                }
            }
            
            # Broadcast a todos los clientes conectados
            asyncio.create_task(self.broadcast_to_group(json.dumps(message), group_id))
            
        except Exception as e:
            print(f"Error al procesar mensaje de Supabase: {e}")
    
    def _handle_supabase_update(self, payload):
        """Manejar actualizaciones de mensajes desde Supabase"""
        try:
            message_data = payload['record']
            group_id = str(message_data['group_id'])
            
            # Crear mensaje para broadcast
            message = {
                "type": "message_updated",
                "data": {
                    "id": str(message_data['id']),
                    "user_id": str(message_data['user_id']),
                    "group_id": str(message_data['group_id']),
                    "message": message_data['message'],
                    "created_at": message_data['created_at'],
                    "status": message_data['status']
                }
            }
            
            # Broadcast a todos los clientes conectados
            asyncio.create_task(self.broadcast_to_group(json.dumps(message), group_id))
            
        except Exception as e:
            print(f"Error al procesar actualización de Supabase: {e}")

# Instancia global del manager
realtime_manager = RealtimeChatManager() 