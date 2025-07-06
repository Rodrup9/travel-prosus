from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.group import Group
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate
from typing import Optional, List
import uuid

class GroupService:
    
    @staticmethod
    def create_group(db: Session, group: GroupCreate) -> Group:
        user = db.query(User).filter(User.id == group.host_id).first()
        if not user:
            raise ValueError("El host_id no existe en la tabla users")
        db_group = Group(
            id=uuid.uuid4(),
            name=group.name,
            host_id=group.host_id,
            status=group.status,
        )
        try:
            db.add(db_group)
            db.commit()
            db.refresh(db_group)
            return db_group
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al crear Grupo: {str(e.orig)}")

    
    @staticmethod
    def get_group_by_id(db: Session, group_id: uuid.UUID) -> Optional[Group]:
        return db.query(Group).filter(Group.id == group_id).first()
    
    @staticmethod
    def get_by_id(db: Session, group_id: uuid.UUID) -> Optional[Group]:
        return db.query(Group).filter(Group.id == group_id).first()
    
    @staticmethod
    def get_groups(db: Session, skip: int = 0, limit: int = 100) -> List[Group]:
        return db.query(Group).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_user(db: Session, user_id: uuid.UUID) -> List[Group]:
        return db.query(Group).filter(Group.host_id == user_id).all()
    
    @staticmethod
    def update_group(db: Session, group_id: uuid.UUID, group_update: GroupUpdate) -> Optional[Group]:
        db_group = db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            return None
        
        update_data = group_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_group, field, value)
        
        try:
            db.commit()
            db.refresh(db_group)
            return db_group
        except IntegrityError:
            db.rollback()
            raise ValueError("Error al actualizar ")
    
    @staticmethod
    def delete_group(db: Session, group_id: uuid.UUID) -> bool:
        db_group = db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            return False
        
        db.delete(db_group)
        db.commit()
        return True
    
    @staticmethod
    def toggle_group_status(db: Session, group_id: uuid.UUID) -> Optional[Group]:
        db_group = db.query(Group).filter(Group.id == group_id).first()
        if not db_group:
            return None
        
        db_group.status = not db_group.status
        db.commit()
        db.refresh(db_group)
        return db_group
    
    @staticmethod
    def get_groups_by_host_id(db: Session, host_id: uuid.UUID) -> List[Group]:
        return db.query(Group).filter(Group.host_id == host_id).all()