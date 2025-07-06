# Guía de Chat en Tiempo Real - Travel ProSus

## Descripción General

Este sistema implementa un chat en tiempo real usando WebSockets y Supabase para proporcionar comunicación instantánea entre usuarios en grupos de viaje. El sistema combina la potencia de FastAPI para el backend con WebSockets para la comunicación en tiempo real y Supabase para la sincronización de datos.

## Arquitectura del Sistema

### Componentes Principales

1. **RealtimeChatManager** (`app/services/realtime_chat.py`)
   - Maneja las conexiones WebSocket activas
   - Gestiona las suscripciones a Supabase
   - Coordina el broadcast de mensajes

2. **WebSocket Router** (`app/routers/websocket_chat.py`)
   - Endpoint WebSocket para conexiones de chat
   - Procesa mensajes entrantes
   - Maneja indicadores de escritura

3. **Cliente JavaScript** (`static/chat_client.js`)
   - Cliente WebSocket para el frontend
   - Maneja reconexión automática
   - Proporciona API simple para integrar

## Configuración

### 1. Variables de Entorno

Asegúrate de tener configuradas las siguientes variables en tu archivo `.env`:

```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_anon_key_de_supabase
```

### 2. Dependencias

Las dependencias necesarias ya están incluidas en `requirements.txt`:

- `websockets==15.0.1` - Para WebSocket
- `supabase==2.16.0` - Cliente de Supabase
- `realtime==2.5.3` - Funcionalidad realtime de Supabase

## Uso del Sistema

### 1. Iniciar el Servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Conectar desde el Frontend

```javascript
// Crear instancia del cliente
const chatClient = new RealtimeChatClient('group-uuid', 'user-uuid');

// Conectar al chat
chatClient.connect();

// Configurar manejadores de eventos
chatClient.onMessage('new_message', (data) => {
    console.log('Nuevo mensaje:', data);
    // Actualizar UI aquí
});

chatClient.onMessage('user_typing', (data) => {
    console.log('Usuario escribiendo:', data.user_id);
    // Mostrar indicador de escritura
});
```

### 3. Enviar Mensajes

```javascript
// Enviar mensaje simple
chatClient.sendMessage('¡Hola a todos!');

// Manejar escritura
chatClient.handleTyping(); // Se llama automáticamente al escribir
```

## Endpoints Disponibles

### WebSocket
- `ws://localhost:8000/ws/chat/{group_id}` - Conexión WebSocket para chat

### REST API
- `GET /chat/{group_id}/connections` - Obtener conexiones activas

## Tipos de Mensajes

### Mensajes Enviados por el Cliente

```json
{
    "type": "send_message",
    "data": {
        "user_id": "uuid-del-usuario",
        "message": "Contenido del mensaje"
    }
}
```

```json
{
    "type": "typing",
    "data": {
        "user_id": "uuid-del-usuario"
    }
}
```

```json
{
    "type": "stop_typing",
    "data": {
        "user_id": "uuid-del-usuario"
    }
}
```

### Mensajes Recibidos del Servidor

```json
{
    "type": "new_message",
    "data": {
        "id": "uuid-del-mensaje",
        "user_id": "uuid-del-usuario",
        "group_id": "uuid-del-grupo",
        "message": "Contenido del mensaje",
        "created_at": "2024-01-01T12:00:00Z",
        "status": true
    }
}
```

```json
{
    "type": "message_sent",
    "data": {
        "id": "uuid-del-mensaje",
        "user_id": "uuid-del-usuario",
        "group_id": "uuid-del-grupo",
        "message": "Contenido del mensaje",
        "created_at": "2024-01-01T12:00:00Z",
        "status": true
    }
}
```

```json
{
    "type": "user_typing",
    "data": {
        "user_id": "uuid-del-usuario",
        "group_id": "uuid-del-grupo"
    }
}
```

```json
{
    "type": "user_stop_typing",
    "data": {
        "user_id": "uuid-del-usuario",
        "group_id": "uuid-del-grupo"
    }
}
```

```json
{
    "type": "error",
    "message": "Descripción del error"
}
```

## Características del Sistema

### 1. Comunicación en Tiempo Real
- Mensajes instantáneos entre usuarios
- Indicadores de escritura en tiempo real
- Sincronización automática con Supabase

### 2. Gestión de Conexiones
- Múltiples conexiones por grupo
- Limpieza automática de conexiones perdidas
- Reconexión automática en el cliente

### 3. Indicadores de Estado
- Estado de conexión visible
- Indicadores de escritura
- Confirmación de mensajes enviados

### 4. Persistencia de Datos
- Todos los mensajes se guardan en la base de datos
- Sincronización bidireccional con Supabase
- Historial completo de conversaciones

## Integración con Supabase

El sistema utiliza Supabase para:

1. **Sincronización de Datos**: Los mensajes se guardan automáticamente en la tabla `group_chat`
2. **Realtime Subscriptions**: Suscripciones a cambios en tiempo real
3. **Escalabilidad**: Manejo eficiente de múltiples grupos y usuarios

### Configuración de Supabase

Asegúrate de que tu tabla `group_chat` tenga la siguiente estructura:

```sql
CREATE TABLE group_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES groups(id),
    message TEXT NOT NULL,
    status BOOLEAN DEFAULT TRUE
);

-- Habilitar realtime para la tabla
ALTER TABLE group_chat REPLICA IDENTITY FULL;
```

## Ejemplo de Implementación Completa

### Frontend (React/Vue/Angular)

```javascript
// Ejemplo con React
import { useEffect, useState } from 'react';

function ChatComponent({ groupId, userId }) {
    const [messages, setMessages] = useState([]);
    const [isConnected, setIsConnected] = useState(false);
    const [typingUsers, setTypingUsers] = useState(new Set());

    useEffect(() => {
        const chatClient = new RealtimeChatClient(groupId, userId);
        
        chatClient.onMessage('new_message', (data) => {
            setMessages(prev => [...prev, data]);
        });
        
        chatClient.onMessage('user_typing', (data) => {
            setTypingUsers(prev => new Set(prev).add(data.user_id));
        });
        
        chatClient.onMessage('user_stop_typing', (data) => {
            setTypingUsers(prev => {
                const newSet = new Set(prev);
                newSet.delete(data.user_id);
                return newSet;
            });
        });
        
        chatClient.onConnection('connected', () => {
            setIsConnected(true);
        });
        
        chatClient.connect();
        
        return () => chatClient.disconnect();
    }, [groupId, userId]);

    const sendMessage = (message) => {
        chatClient.sendMessage(message);
    };

    return (
        <div className="chat-container">
            <div className="connection-status">
                {isConnected ? 'Conectado' : 'Desconectado'}
            </div>
            
            <div className="messages">
                {messages.map(msg => (
                    <div key={msg.id} className="message">
                        {msg.message}
                    </div>
                ))}
            </div>
            
            {typingUsers.size > 0 && (
                <div className="typing-indicator">
                    {typingUsers.size} usuario(s) escribiendo...
                </div>
            )}
            
            <MessageInput onSend={sendMessage} />
        </div>
    );
}
```

## Consideraciones de Seguridad

1. **Autenticación**: Implementa autenticación JWT para validar usuarios
2. **Autorización**: Verifica que el usuario pertenezca al grupo antes de permitir conexión
3. **Rate Limiting**: Implementa límites de velocidad para evitar spam
4. **Validación**: Valida todos los mensajes entrantes

## Monitoreo y Debugging

### Logs del Servidor
```python
# En el código del servidor
print(f"Usuario {user_id} conectado al grupo {group_id}")
print(f"Mensaje recibido: {message}")
```

### Estado de Conexiones
```bash
curl http://localhost:8000/chat/{group_id}/connections
```

### Cliente JavaScript
```javascript
// Verificar estado de conexión
console.log(chatClient.getConnectionStatus());

// Debug de mensajes
chatClient.onMessage('*', (message) => {
    console.log('Mensaje recibido:', message);
});
```

## Escalabilidad

El sistema está diseñado para escalar horizontalmente:

1. **Múltiples Instancias**: Puedes ejecutar múltiples instancias del servidor
2. **Load Balancer**: Usa un load balancer para distribuir conexiones
3. **Redis**: Considera usar Redis para compartir estado entre instancias
4. **Supabase**: Maneja la sincronización de datos automáticamente

## Troubleshooting

### Problemas Comunes

1. **Conexión Rechazada**
   - Verifica que el servidor esté ejecutándose
   - Confirma la URL del WebSocket
   - Revisa los logs del servidor

2. **Mensajes No Llegan**
   - Verifica la configuración de Supabase
   - Confirma que las suscripciones estén activas
   - Revisa los permisos de la base de datos

3. **Conexiones Perdidas**
   - Implementa reconexión automática
   - Verifica la estabilidad de la red
   - Monitorea el uso de memoria del servidor

### Debugging

```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)
```

```javascript
// Debug en el cliente
chatClient.websocket.onerror = (error) => {
    console.error('Error de WebSocket:', error);
};
```

## Conclusión

Este sistema de chat en tiempo real proporciona una base sólida para la comunicación en grupos de viaje. Con la integración de WebSockets, Supabase y FastAPI, obtienes un sistema escalable, confiable y fácil de mantener.

Para más información o soporte, consulta la documentación de FastAPI, WebSockets y Supabase. 