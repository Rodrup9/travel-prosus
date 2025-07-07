from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.group_member import GroupMemberCreate, GroupMemberUpdate, GroupMemberResponse
from app.services.group_member import GroupMemberService
from app.database import get_db
import uuid
from typing import List

router = APIRouter(
    prefix="/group-members",
    tags=["Group Members"]
)

@router.post("/", response_model=GroupMemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(member: GroupMemberCreate, db: Session = Depends(get_db)):
    try:
        return GroupMemberService.create_member(db, member)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[GroupMemberResponse])
def get_all_members(db: Session = Depends(get_db)):
    return GroupMemberService.get_members(db)

@router.get("/user/{user_id}", response_model=List[GroupMemberResponse])
def get_members_by_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    return GroupMemberService.get_members_by_user(db, user_id)

@router.get("/{group_id}/{user_id}", response_model=GroupMemberResponse)
def get_member_by_ids(group_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    member = GroupMemberService.get_member_by_ids(db, group_id, user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return member

@router.put("/{group_id}/{user_id}", response_model=GroupMemberResponse)
def update_member(group_id: uuid.UUID, user_id: uuid.UUID, member_update: GroupMemberUpdate, db: Session = Depends(get_db)):
    updated = GroupMemberService.update_member(db, group_id, user_id, member_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return updated

@router.delete("/{group_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(group_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    deleted = GroupMemberService.delete_member(db, group_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return

@router.patch("/{group_id}/{user_id}/toggle-status", response_model=GroupMemberResponse)
def toggle_member_status(group_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    toggled = GroupMemberService.toggle_member_status(db, group_id, user_id)
    if not toggled:
        raise HTTPException(status_code=404, detail="Miembro no encontrado")
    return toggled
