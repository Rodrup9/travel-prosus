class RealtimeChatClient {
    constructor(groupId, userId, serverUrl = 'ws://localhost:8000') {
        this.groupId = groupId;
        this.userId = userId;
        this.serverUrl = serverUrl;
        this.websocket = null;
        this.isConnected = false;
        this.typingTimeout = null;
        this.messageHandlers = new Map();
        this.connectionHandlers = new Map();
    }

    // Conectar al WebSocket
    connect() {
        try {
            this.websocket = new WebSocket(`${this.serverUrl}/ws/chat/${this.groupId}`);
            
            this.websocket.onopen = () => {
                console.log('Conectado al chat en tiempo real');
                this.isConnected = true;
                this.triggerConnectionHandlers('connected');
            };

            this.websocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleMessage(message);
            };

            this.websocket.onclose = () => {
                console.log('Desconectado del chat');
                this.isConnected = false;
                this.triggerConnectionHandlers('disconnected');
            };

            this.websocket.onerror = (error) => {
                console.error('Error en WebSocket:', error);
                this.triggerConnectionHandlers('error', error);
            };

        } catch (error) {
            console.error('Error al conectar:', error);
        }
    }

    // Desconectar del WebSocket
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
            this.isConnected = false;
        }
    }

    // Enviar mensaje
    sendMessage(message) {
        if (!this.isConnected) {
            console.error('No conectado al WebSocket');
            return false;
        }

        const messageData = {
            type: 'send_message',
            data: {
                user_id: this.userId,
                message: message
            }
        };

        this.websocket.send(JSON.stringify(messageData));
        return true;
    }

    // Indicar que el usuario está escribiendo
    startTyping() {
        if (!this.isConnected) return;

        const typingData = {
            type: 'typing',
            data: {
                user_id: this.userId
            }
        };

        this.websocket.send(JSON.stringify(typingData));
    }

    // Indicar que el usuario dejó de escribir
    stopTyping() {
        if (!this.isConnected) return;

        const stopTypingData = {
            type: 'stop_typing',
            data: {
                user_id: this.userId
            }
        };

        this.websocket.send(JSON.stringify(stopTypingData));
    }

    // Manejar escritura con debounce
    handleTyping() {
        this.startTyping();
        
        // Limpiar timeout anterior
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // Detener escritura después de 2 segundos
        this.typingTimeout = setTimeout(() => {
            this.stopTyping();
        }, 2000);
    }

    // Manejar mensajes recibidos
    handleMessage(message) {
        const messageType = message.type;
        
        if (this.messageHandlers.has(messageType)) {
            this.messageHandlers.get(messageType)(message.data);
        } else {
            console.log('Mensaje recibido:', message);
        }
    }

    // Registrar manejadores de mensajes
    onMessage(type, handler) {
        this.messageHandlers.set(type, handler);
    }

    // Registrar manejadores de conexión
    onConnection(type, handler) {
        this.connectionHandlers.set(type, handler);
    }

    // Disparar manejadores de conexión
    triggerConnectionHandlers(type, data = null) {
        if (this.connectionHandlers.has(type)) {
            this.connectionHandlers.get(type)(data);
        }
    }

    // Verificar estado de conexión
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            groupId: this.groupId,
            userId: this.userId
        };
    }
}

// Ejemplo de uso:
/*
const chatClient = new RealtimeChatClient('group-uuid', 'user-uuid');

// Conectar al chat
chatClient.connect();

// Manejar nuevos mensajes
chatClient.onMessage('new_message', (data) => {
    console.log('Nuevo mensaje:', data);
    // Aquí puedes actualizar la UI
});

// Manejar mensajes enviados
chatClient.onMessage('message_sent', (data) => {
    console.log('Mensaje enviado:', data);
    // Aquí puedes mostrar confirmación
});

// Manejar usuarios escribiendo
chatClient.onMessage('user_typing', (data) => {
    console.log('Usuario escribiendo:', data.user_id);
    // Aquí puedes mostrar indicador de escritura
});

// Manejar usuarios que dejaron de escribir
chatClient.onMessage('user_stop_typing', (data) => {
    console.log('Usuario dejó de escribir:', data.user_id);
    // Aquí puedes ocultar indicador de escritura
});

// Manejar errores
chatClient.onMessage('error', (data) => {
    console.error('Error:', data.message);
    // Aquí puedes mostrar error al usuario
});

// Manejar cambios de conexión
chatClient.onConnection('connected', () => {
    console.log('Conectado al chat');
});

chatClient.onConnection('disconnected', () => {
    console.log('Desconectado del chat');
});

// Enviar mensaje
function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;
    
    if (message.trim()) {
        chatClient.sendMessage(message);
        messageInput.value = '';
    }
}

// Manejar escritura
function handleTyping() {
    chatClient.handleTyping();
}

// Desconectar al salir
window.addEventListener('beforeunload', () => {
    chatClient.disconnect();
});
*/ 