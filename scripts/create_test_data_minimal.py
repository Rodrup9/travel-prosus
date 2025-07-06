#!/usr/bin/env python3
"""
Script minimalista para crear datos de prueba en la base de datos
Ejecutar: python scripts/create_test_data_minimal.py
"""

import sys
import os
import uuid
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from sqlalchemy import text

def create_test_data():
    """Crear datos de prueba usando SQL directo para evitar problemas de relaciones"""
    db = SessionLocal()
    
    try:
        print("Creando datos de prueba...")
        
        # Crear usuarios de prueba usando SQL directo
        users = []
        user_data = [
            ("Juan Pérez", "juan@example.com"),
            ("María García", "maria@example.com"),
            ("Carlos López", "carlos@example.com"),
            ("Ana Martínez", "ana@example.com"),
            ("Luis Rodríguez", "luis@example.com")
        ]
        
        for name, email in user_data:
            # Verificar si el usuario ya existe
            result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"Usuario {email} ya existe")
                users.append({"id": existing_user[0], "name": name, "email": email})
                continue
            
            user_id = str(uuid.uuid4())
            db.execute(
                text("""
                    INSERT INTO users (id, name, email, status, created_at) 
                    VALUES (:id, :name, :email, :status, :created_at)
                """),
                {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "status": True,
                    "created_at": datetime.now()
                }
            )
            users.append({"id": user_id, "name": name, "email": email})
            print(f"Usuario creado: {name} ({email})")
        
        # Crear grupos de prueba
        groups = []
        group_data = [
            ("Viaje a París", users[0]["id"]),
            ("Aventura en Tokio", users[1]["id"]),
            ("Playa en Cancún", users[2]["id"])
        ]
        
        for name, host_id in group_data:
            # Verificar si el grupo ya existe
            result = db.execute(text("SELECT id FROM groups WHERE name = :name"), {"name": name})
            existing_group = result.fetchone()
            
            if existing_group:
                print(f"Grupo {name} ya existe")
                groups.append({"id": existing_group[0], "name": name, "host_id": host_id})
                continue
            
            group_id = str(uuid.uuid4())
            db.execute(
                text("""
                    INSERT INTO groups (id, name, host_id, status, created_at) 
                    VALUES (:id, :name, :host_id, :status, :created_at)
                """),
                {
                    "id": group_id,
                    "name": name,
                    "host_id": host_id,
                    "status": True,
                    "created_at": datetime.now()
                }
            )
            groups.append({"id": group_id, "name": name, "host_id": host_id})
            print(f"Grupo creado: {name}")
        
        # Crear algunos mensajes de prueba
        test_messages = [
            (groups[0]["id"], users[0]["id"], "¡Hola a todos! ¿Cómo están?"),
            (groups[0]["id"], users[1]["id"], "¡Hola Juan! Todo bien, ¿y tú?"),
            (groups[0]["id"], users[2]["id"], "¡Excelente! Ya estoy listo para el viaje"),
            (groups[1]["id"], users[1]["id"], "Bienvenidos al grupo de Tokio"),
            (groups[1]["id"], users[3]["id"], "¡Gracias! Estoy muy emocionada"),
            (groups[2]["id"], users[2]["id"], "¿Quién ya tiene reservas de hotel?"),
            (groups[2]["id"], users[4]["id"], "Yo ya tengo todo listo")
        ]
        
        for group_id, user_id, message in test_messages:
            message_id = str(uuid.uuid4())
            db.execute(
                text("""
                    INSERT INTO group_chat (id, user_id, group_id, message, status, created_at) 
                    VALUES (:id, :user_id, :group_id, :message, :status, :created_at)
                """),
                {
                    "id": message_id,
                    "user_id": user_id,
                    "group_id": group_id,
                    "message": message,
                    "status": True,
                    "created_at": datetime.now()
                }
            )
            print(f"Mensaje creado: {message[:30]}...")
        
        # Commit de todos los cambios
        db.commit()
        print("\n✅ Datos de prueba creados exitosamente!")
        
        # Mostrar resumen
        print("\n📊 Resumen de datos creados:")
        print(f"   Usuarios: {len(users)}")
        print(f"   Grupos: {len(groups)}")
        print(f"   Mensajes: {len(test_messages)}")
        
        print("\n🔑 IDs importantes para probar el chat:")
        if users:
            print(f"   Usuario 1: {users[0]['id']} ({users[0]['name']})")
            print(f"   Usuario 2: {users[1]['id']} ({users[1]['name']})")
        if groups:
            print(f"   Grupo 1: {groups[0]['id']} ({groups[0]['name']})")
            print(f"   Grupo 2: {groups[1]['id']} ({groups[1]['name']})")
        
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