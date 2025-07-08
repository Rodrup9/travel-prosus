# app/routers/group_chat_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from app.schemas.group_chat import GroupChatCreate, GroupChatUpdate, GroupChatResponse
from app.services.group_chat import GroupChatService
from app.database import get_db

router = APIRouter(prefix="/group-chat", tags=["Group Chat"])


@router.post("/", response_model=GroupChatResponse)
async def create_group_chat(group_chat: GroupChatCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await GroupChatService.create_group_chat(db, group_chat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[GroupChatResponse])
async def get_all_group_chats(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await GroupChatService.get_group_chats(db, skip=skip, limit=limit)


@router.get("/{group_chat_id}", response_model=GroupChatResponse)
async def get_group_chat_by_id(group_chat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    group_chat = await GroupChatService.get_group_chat_by_id(db, group_chat_id)
    if not group_chat:
        raise HTTPException(status_code=404, detail="Chat de grupo no encontrado")
    return group_chat


@router.get("/group/{group_id}", response_model=List[GroupChatResponse])
async def get_group_chats_by_group(group_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await GroupChatService.get_group_chats_by_group(db, group_id)


@router.put("/{group_chat_id}", response_model=GroupChatResponse)
async def update_group_chat(group_chat_id: uuid.UUID, group_chat_update: GroupChatUpdate, db: AsyncSession = Depends(get_db)):
    updated_group_chat = await GroupChatService.update_group_chat(db, group_chat_id, group_chat_update)
    if not updated_group_chat:
        raise HTTPException(status_code=404, detail="Chat de grupo no encontrado")
    return updated_group_chat


@router.delete("/{group_chat_id}")
async def delete_group_chat(group_chat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    deleted = await GroupChatService.delete_group_chat(db, group_chat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat de grupo no encontrado")
    return {"message": "Chat de grupo eliminado correctamente"}


@router.patch("/{group_chat_id}/toggle-status", response_model=GroupChatResponse)
async def toggle_status(group_chat_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    group_chat = await GroupChatService.toggle_status(db, group_chat_id)
    if not group_chat:
        raise HTTPException(status_code=404, detail="Chat de grupo no encontrado")
    return group_chat
