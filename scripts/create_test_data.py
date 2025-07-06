#!/usr/bin/env python3
"""
Script para crear datos de prueba en la base de datos
Ejecutar: python scripts/create_test_data.py
"""

import sys
import os
import uuid
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.user import User
from app.models.group import Group
from app.models.group_chat import GroupChat

def create_test_data():
    """Crear datos de prueba en la base de datos"""
    db = SessionLocal()
    
    try:
        print("Creando datos de prueba...")
        
        # Crear usuarios de prueba
        users = []
        user_data = [
            {"name": "Juan Pérez", "email": "juan@example.com"},
            {"name": "María García", "email": "maria@example.com"},
            {"name": "Carlos López", "email": "carlos@example.com"},
            {"name": "Ana Martínez", "email": "ana@example.com"},
            {"name": "Luis Rodríguez", "email": "luis@example.com"}
        ]
        
        for user_info in user_data:
            # Verificar si el usuario ya existe
            existing_user = db.query(User).filter(User.email == user_info["email"]).first()
            if existing_user:
                print(f"Usuario {user_info['email']} ya existe")
                users.append(existing_user)
                continue
                
            user = User(
                id=uuid.uuid4(),
                name=user_info["name"],
                email=user_info["email"],
                status=True,
                created_at=datetime.now()
            )
            db.add(user)
            users.append(user)
            print(f"Usuario creado: {user_info['name']} ({user.email})")
        
        # Crear grupos de prueba
        groups = []
        group_data = [
            {"name": "Viaje a París", "host": users[0]},
            {"name": "Aventura en Tokio", "host": users[1]},
            {"name": "Playa en Cancún", "host": users[2]}
        ]
        
        for group_info in group_data:
            # Verificar si el grupo ya existe
            existing_group = db.query(Group).filter(Group.name == group_info["name"]).first()
            if existing_group:
                print(f"Grupo {group_info['name']} ya existe")
                groups.append(existing_group)
                continue
                
            group = Group(
                id=uuid.uuid4(),
                name=group_info["name"],
                host_id=group_info["host"].id,
                status=True,
                created_at=datetime.now()
            )
            db.add(group)
            groups.append(group)
            print(f"Grupo creado: {group_info['name']} (Host: {group_info['host'].name})")
        
        # Crear algunos mensajes de prueba
        if groups and users:
            test_messages = [
                {"group": groups[0], "user": users[0], "message": "¡Hola a todos! ¿Cómo están?"},
                {"group": groups[0], "user": users[1], "message": "¡Hola Juan! Todo bien, ¿y tú?"},
                {"group": groups[0], "user": users[2], "message": "¡Excelente! Ya estoy listo para el viaje"},
                {"group": groups[1], "user": users[1], "message": "Bienvenidos al grupo de Tokio"},
                {"group": groups[1], "user": users[3], "message": "¡Gracias! Estoy muy emocionada"},
                {"group": groups[2], "user": users[2], "message": "¿Quién ya tiene reservas de hotel?"},
                {"group": groups[2], "user": users[4], "message": "Yo ya tengo todo listo"}
            ]
            
            for msg_info in test_messages:
                message = GroupChat(
                    id=uuid.uuid4(),
                    user_id=msg_info["user"].id,
                    group_id=msg_info["group"].id,
                    message=msg_info["message"],
                    status=True,
                    created_at=datetime.now()
                )
                db.add(message)
                print(f"Mensaje creado en {msg_info['group'].name}: {msg_info['message'][:30]}...")
        
        # Commit de todos los cambios
        db.commit()
        print("\n✅ Datos de prueba creados exitosamente!")
        
        # Mostrar resumen
        print("\n📊 Resumen de datos creados:")
        print(f"   Usuarios: {len(users)}")
        print(f"   Grupos: {len(groups)}")
        print(f"   Mensajes: {len(test_messages) if 'test_messages' in locals() else 0}")
        
        print("\n🔑 IDs importantes para probar el chat:")
        if users:
            print(f"   Usuario 1: {users[0].id} ({users[0].name})")
            print(f"   Usuario 2: {users[1].id} ({users[1].name})")
        if groups:
            print(f"   Grupo 1: {groups[0].id} ({groups[0].name})")
            print(f"   Grupo 2: {groups[1].id} ({groups[1].name})")
        
        print("\n🌐 Para probar el chat:")
        print("   1. Inicia el servidor: uvicorn app.main:app --reload")
        print("   2. Abre: static/chat_example_improved.html")
        print("   3. Selecciona un grupo y usuario de la lista")
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data() 