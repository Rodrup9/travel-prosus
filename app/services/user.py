from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List
import uuid

class UserService:
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Crear un nuevo usuario"""
        db_user = User(
            id=uuid.uuid4(),
            name=user.name,
            email=user.email,
            status=user.status,
            avatar_url=user.avatar_url
        )
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("El email ya está registrado")
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Obtener usuario por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener lista de usuarios"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
        """Actualizar usuario"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("El email ya está registrado")
    
    @staticmethod
    def delete_user(db: Session, user_id: uuid.UUID) -> bool:
        """Eliminar usuario"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def toggle_user_status(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Cambiar el estado del usuario"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        db_user.status = not db_user.status
        db.commit()
        db.refresh(db_user)
        return db_user