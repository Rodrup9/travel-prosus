from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.group_member import GroupMember
from app.schemas.group_member import GroupMemberCreate, GroupMemberUpdate
from typing import Optional, List
import uuid

class GroupMemberService:

    @staticmethod
    def create_member(db: Session, member: GroupMemberCreate) -> GroupMember:
        db_member = GroupMember(
            id=uuid.uuid4(),
            group_id=member.group_id,
            user_id=member.user_id,
            status=member.status
        )
        try:
            db.add(db_member)
            db.commit()
            db.refresh(db_member)
            return db_member
        except IntegrityError:
            db.rollback()
            raise ValueError("Ya existe este miembro en el grupo o claves inválidas")

    @staticmethod
    def get_member_by_id(db: Session, member_id: uuid.UUID) -> Optional[GroupMember]:
        return db.query(GroupMember).filter(GroupMember.id == member_id).first()

    @staticmethod
    def get_members(db: Session, skip: int = 0, limit: int = 100) -> List[GroupMember]:
        return db.query(GroupMember).offset(skip).limit(limit).all()

    @staticmethod
    def update_member(db: Session, member_id: uuid.UUID, member_update: GroupMemberUpdate) -> Optional[GroupMember]:
        db_member = db.query(GroupMember).filter(GroupMember.id == member_id).first()
        if not db_member:
            return None

        update_data = member_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_member, field, value)

        try:
            db.commit()
            db.refresh(db_member)
            return db_member
        except IntegrityError:
            db.rollback()
            raise ValueError("Error al actualizar miembro del grupo")

    @staticmethod
    def delete_member(db: Session, member_id: uuid.UUID) -> bool:
        db_member = db.query(GroupMember).filter(GroupMember.id == member_id).first()
        if not db_member:
            return False

        db.delete(db_member)
        db.commit()
        return True

    @staticmethod
    def toggle_member_status(db: Session, member_id: uuid.UUID) -> Optional[GroupMember]:
        db_member = db.query(GroupMember).filter(GroupMember.id == member_id).first()
        if not db_member:
            return None

        db_member.status = not db_member.status
        db.commit()
        db.refresh(db_member)
        return db_member