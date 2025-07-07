from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.services.realtime_chat import realtime_manager
from app.services.group_chat import GroupChatService
from app.schemas.group_chat import GroupChatCreate
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.group import Group
from app.models.user import User
import json
import uuid
from typing import List

router = APIRouter()

@router.websocket("/ws/chat/{group_id}")
async def websocket_endpoint(websocket: WebSocket, group_id: str):
    await realtime_manager.connect(websocket, group_id)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Validar que el mensaje tenga la estructura correcta
            if message_data.get("type") == "send_message":
                chat_data = message_data.get("data", {})
                
                # Crear el mensaje en la base de datos
                chat_create = GroupChatCreate(
                    user_id=uuid.UUID(chat_data["user_id"]),
                    group_id=uuid.UUID(group_id),
                    message=chat_data["message"]
                )
                
                # Guardar en la base de datos usando el servicio existente
                db = next(get_db())
                try:
                    new_message = GroupChatService.create_message(db, chat_create)
                    
                    # Obtener información del usuario
                    user = db.query(User).filter(User.id == new_message.user_id).first()
                    user_name = user.name if user else "Usuario desconocido"
                    
                    # Crear respuesta para confirmar el mensaje
                    response = {
                        "type": "message_sent",
                        "data": {
                            "id": str(new_message.id),
                            "user_id": str(new_message.user_id),
                            "group_id": str(new_message.group_id),
                            "message": new_message.message,
                            "created_at": new_message.created_at.isoformat(),
                            "status": new_message.status,
                            "user_name": user_name
                        }
                    }
                    
                    # Enviar confirmación al remitente
                    await realtime_manager.send_personal_message(
                        json.dumps(response), 
                        websocket
                    )
                    
                    # Broadcast del nuevo mensaje a todos los clientes del grupo
                    await realtime_manager.broadcast_new_message(
                        {
                            "id": str(new_message.id),
                            "user_id": str(new_message.user_id),
                            "group_id": str(new_message.group_id),
                            "message": new_message.message,
                            "created_at": new_message.created_at.isoformat(),
                            "status": new_message.status,
                            "user_name": user_name
                        },
                        group_id
                    )
                    
                except Exception as e:
                    # Enviar error al cliente
                    error_response = {
                        "type": "error",
                        "message": str(e)
                    }
                    await realtime_manager.send_personal_message(
                        json.dumps(error_response), 
                        websocket
                    )
                finally:
                    db.close()
            
            elif message_data.get("type") == "typing":
                # Broadcast de indicador de escritura
                typing_message = {
                    "type": "user_typing",
                    "data": {
                        "user_id": message_data["data"]["user_id"],
                        "group_id": group_id
                    }
                }
                await realtime_manager.broadcast_to_group(
                    json.dumps(typing_message), 
                    group_id, 
                    exclude_websocket=websocket
                )
            
            elif message_data.get("type") == "stop_typing":
                # Broadcast de fin de escritura
                stop_typing_message = {
                    "type": "user_stop_typing",
                    "data": {
                        "user_id": message_data["data"]["user_id"],
                        "group_id": group_id
                    }
                }
                await realtime_manager.broadcast_to_group(
                    json.dumps(stop_typing_message), 
                    group_id, 
                    exclude_websocket=websocket
                )
    
    except WebSocketDisconnect:
        realtime_manager.disconnect(websocket, group_id)
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        realtime_manager.disconnect(websocket, group_id)

@router.get("/chat/{group_id}/connections")
async def get_active_connections(group_id: str):
    """Obtener el número de conexiones activas para un grupo"""
    connections = realtime_manager.active_connections.get(group_id, set())
    return {
        "group_id": group_id,
        "active_connections": len(connections)
    }

@router.get("/chat/groups/{group_id}/members", response_model=List[dict])
async def get_group_members(group_id: str, db: Session = Depends(get_db)):
    """Obtener miembros de un grupo específico"""
    try:
        group_uuid = uuid.UUID(group_id)
        group = db.query(Group).filter(Group.id == group_uuid).first()
        
        if not group:
            raise HTTPException(status_code=404, detail="Grupo no encontrado")
        
        # Obtener el host del grupo
        host = db.query(User).filter(User.id == group.host_id).first()
        if host:
            members = [{
                "id": str(host.id),
                "name": host.name,
                "email": host.email,
                "role": "host"
            }]
        else:
            members = []
        
        # Obtener otros miembros del grupo (si tienes tabla group_members)
        # Aquí puedes agregar lógica adicional para obtener miembros
        
        return members
        
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de grupo inválido") 