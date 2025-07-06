from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.ia_chat import IAChatCreate, IAChatUpdate, IAChatResponse
from app.services.ia_chat import IAChatService
from app.database import get_db
import uuid
from typing import List

router = APIRouter(prefix="/ia_chat", tags=["IA Chat"])

@router.post("/", response_model=IAChatResponse, status_code=status.HTTP_201_CREATED)
def create_message(chat: IAChatCreate, db: Session = Depends(get_db)):
    try:
        return IAChatService.create_message(db, chat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[IAChatResponse])
def get_all_messages(db: Session = Depends(get_db)):
    return IAChatService.get_all_messages(db)

@router.get("/{message_id}", response_model=IAChatResponse)
def get_message_by_id(message_id: uuid.UUID, db: Session = Depends(get_db)):
    message = IAChatService.get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return message

@router.put("/{message_id}", response_model=IAChatResponse)
def update_message(message_id: uuid.UUID, chat_update: IAChatUpdate, db: Session = Depends(get_db)):
    updated = IAChatService.update_message(db, message_id, chat_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return updated

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = IAChatService.delete_message(db, message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return

@router.patch("/{message_id}/toggle", response_model=IAChatResponse)
def toggle_status(message_id: uuid.UUID, db: Session = Depends(get_db)):
    toggled = IAChatService.toggle_status(db, message_id)
    if not toggled:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return toggled

@router.get("/user/{user_id}", response_model=List[IAChatResponse])
def get_messages_by_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return IAChatService.get_messages_by_user(db, user_id)

@router.get("/group/{group_id}", response_model=List[IAChatResponse])
def get_messages_by_group(group_id: uuid.UUID, db: Session = Depends(get_db)):
    return IAChatService.get_messages_by_group(db, group_id)

@router.get("/user/{user_id}/group/{group_id}", response_model=List[IAChatResponse])
def get_messages_by_user_and_group(user_id: uuid.UUID, group_id: uuid.UUID, db: Session = Depends(get_db)):
    return IAChatService.get_messages_by_user_and_group(db, user_id, group_id)
