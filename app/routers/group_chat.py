from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.group_chat import GroupChatService
from app.schemas.group_chat import GroupChatCreate, GroupChatUpdate, GroupChatResponse
from app.database import get_db
from typing import List
import uuid

router = APIRouter(prefix="/group-chat", tags=["Group Chat"])

@router.post("/", response_model=GroupChatResponse, status_code=status.HTTP_201_CREATED)
def create_message(chat: GroupChatCreate, db: Session = Depends(get_db)):
    try:
        return GroupChatService.create_message(db, chat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[GroupChatResponse])
def get_all_messages(db: Session = Depends(get_db)):
    return GroupChatService.get_all_messages(db)

@router.get("/{message_id}", response_model=GroupChatResponse)
def get_message_by_id(message_id: uuid.UUID, db: Session = Depends(get_db)):
    message = GroupChatService.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return message

@router.get("/group/{group_id}", response_model=List[GroupChatResponse])
def get_messages_by_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    return GroupChatService.get_messages_by_group(db, group_id)

@router.get("/group/{group_id}/user/{user_id}", response_model=List[GroupChatResponse])
def get_user_messages_in_group(group_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    return GroupChatService.get_user_messages_in_group(db, group_id, user_id)

@router.put("/{message_id}", response_model=GroupChatResponse)
def update_message(message_id: uuid.UUID, chat_update: GroupChatUpdate, db: Session = Depends(get_db)):
    updated = GroupChatService.update_message(db, message_id, chat_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return updated

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = GroupChatService.delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return

@router.patch("/{message_id}/toggle", response_model=GroupChatResponse)
def toggle_message_status(message_id: uuid.UUID, db: Session = Depends(get_db)):
    message = GroupChatService.toggle_status(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return message
