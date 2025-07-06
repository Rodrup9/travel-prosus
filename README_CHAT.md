# Chat en Tiempo Real - Travel ProSus

## 🚀 Configuración Rápida

### 1. Crear Datos de Prueba

Primero, necesitas crear algunos usuarios y grupos en la base de datos para probar el chat:

```bash
# Ejecutar el script de datos de prueba (versión minimalista)
python scripts/create_test_data_minimal.py
```

Este script creará:
- 5 usuarios de prueba
- 3 grupos de viaje
- Algunos mensajes de ejemplo

### 2. Iniciar el Servidor

```bash
# Iniciar el servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Probar el Chat

Abre el archivo `static/chat_example_improved.html` en tu navegador. Este archivo:

- ✅ Carga automáticamente los grupos y usuarios de la base de datos
- ✅ Permite seleccionar desde dropdowns
- ✅ Muestra nombres reales en lugar de UUIDs
- ✅ Tiene interfaz mejorada y moderna

## 🔧 Configuración Detallada

### Variables de Entorno

Asegúrate de tener configurado tu archivo `.env`:

```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_anon_key_de_supabase
DATABASE_URL=tu_url_de_postgresql
```

### Estructura de la Base de Datos

El sistema utiliza estas tablas:

```sql
-- Tabla de usuarios
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    avatar_url VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de grupos
CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    host_id UUID REFERENCES users(id),
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de mensajes del chat
CREATE TABLE group_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES groups(id),
    message TEXT NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Cómo Usar el Chat

### 1. Conectar al Chat

```javascript
// Crear cliente de chat
const chatClient = new RealtimeChatClient('group-uuid', 'user-uuid');

// Conectar
chatClient.connect();

// Configurar manejadores
chatClient.onMessage('new_message', (data) => {
    console.log('Nuevo mensaje:', data);
});
```

### 2. Enviar Mensajes

```javascript
// Enviar mensaje
chatClient.sendMessage('¡Hola a todos!');

// Indicar que estás escribiendo
chatClient.handleTyping();
```

### 3. Manejar Eventos

```javascript
// Nuevos mensajes
chatClient.onMessage('new_message', (data) => {
    // Actualizar UI con nuevo mensaje
});

// Usuario escribiendo
chatClient.onMessage('user_typing', (data) => {
    // Mostrar indicador de escritura
});

// Errores
chatClient.onMessage('error', (data) => {
    // Mostrar error al usuario
});
```

## 🌐 Endpoints Disponibles

### WebSocket
- `ws://localhost:8000/ws/chat/{group_id}` - Conexión de chat

### REST API
- `GET /chat/groups` - Obtener todos los grupos
- `GET /chat/users` - Obtener todos los usuarios
- `GET /chat/{group_id}/connections` - Ver conexiones activas
- `GET /chat/groups/{group_id}/members` - Ver miembros del grupo

## 🔍 Solución de Problemas

### El chat no funciona

1. **Verifica que el servidor esté ejecutándose:**
   ```bash
   curl http://localhost:8000/chat/groups
   ```

2. **Verifica que hay datos en la base de datos:**
   ```bash
   python scripts/create_test_data_minimal.py
   ```

3. **Revisa la consola del navegador** para errores de JavaScript

4. **Verifica la URL del WebSocket** en el formulario de configuración

### No aparecen grupos/usuarios

1. **Ejecuta el script de datos de prueba:**
   ```bash
   python scripts/create_test_data_minimal.py
   ```

2. **Verifica la conexión a la base de datos**

3. **Revisa los logs del servidor** para errores

### Mensajes no llegan

1. **Verifica que ambos navegadores estén conectados al mismo grupo**

2. **Revisa la configuración de Supabase**

3. **Verifica que los UUIDs sean válidos**

## 📱 Integración en tu Aplicación

### React/Vue/Angular

```javascript
// Ejemplo con React
import { useEffect, useState } from 'react';

function ChatComponent({ groupId, userId }) {
    const [messages, setMessages] = useState([]);
    const [chatClient, setChatClient] = useState(null);

    useEffect(() => {
        const client = new RealtimeChatClient(groupId, userId);
        
        client.onMessage('new_message', (data) => {
            setMessages(prev => [...prev, data]);
        });
        
        client.connect();
        setChatClient(client);
        
        return () => client.disconnect();
    }, [groupId, userId]);

    const sendMessage = (message) => {
        if (chatClient) {
            chatClient.sendMessage(message);
        }
    };

    return (
        <div className="chat-container">
            {/* Tu UI aquí */}
        </div>
    );
}
```

### Autenticación

Para agregar autenticación, modifica el WebSocket endpoint:

```python
@router.websocket("/ws/chat/{group_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    group_id: str, 
    token: str = Query(...)
):
    # Verificar token JWT
    user = verify_jwt_token(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # Verificar que el usuario pertenece al grupo
    if not user_belongs_to_group(user.id, group_id):
        await websocket.close(code=4003, reason="Forbidden")
        return
    
    await realtime_manager.connect(websocket, group_id)
    # ... resto del código
```

## 🚀 Características Avanzadas

### 1. Indicadores de Escritura
- Se muestran automáticamente cuando alguien escribe
- Se ocultan después de 2 segundos de inactividad

### 2. Reconexión Automática
- El cliente se reconecta automáticamente si pierde conexión
- Mantiene el estado de los mensajes

### 3. Múltiples Grupos
- Puedes tener múltiples chats abiertos simultáneamente
- Cada grupo tiene su propia sala de chat

### 4. Persistencia
- Todos los mensajes se guardan en la base de datos
- Historial completo disponible

## 🔒 Seguridad

### Recomendaciones

1. **Implementa autenticación JWT**
2. **Verifica permisos de grupo**
3. **Valida mensajes entrantes**
4. **Implementa rate limiting**
5. **Usa HTTPS en producción**

### Ejemplo de Validación

```python
def validate_message(message: str) -> bool:
    """Validar mensaje antes de procesarlo"""
    if len(message.strip()) == 0:
        return False
    if len(message) > 1000:  # Límite de caracteres
        return False
    # Agregar más validaciones según necesites
    return True
```

## 📊 Monitoreo

### Verificar Estado

```bash
# Ver conexiones activas
curl http://localhost:8000/chat/{group_id}/connections

# Ver grupos disponibles
curl http://localhost:8000/chat/groups

# Ver usuarios disponibles
curl http://localhost:8000/chat/users
```

### Logs del Servidor

```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎉 ¡Listo!

Con estos pasos ya tienes un chat en tiempo real completamente funcional. El sistema es escalable y puede manejar múltiples grupos y usuarios simultáneamente.

Para más información, consulta la documentación completa en `docs/realtime_chat_guide.md`. 