# Integración del Agente de IA para Viajes

## Resumen de Mejoras Implementadas

### 1. Integración Completa del TripPlannerAgent

**Antes:**
- Solo se usaba el modelo Groq directamente
- No había integración con herramientas especializadas
- No se guardaban resultados en la base de datos

**Después:**
- Integración completa del `TripPlannerAgent` especializado
- Uso de herramientas de búsqueda de vuelos y hoteles (Amadeus API)
- Guardado automático de itinerarios, vuelos y hoteles en la base de datos

### 2. Manejo Mejorado del Historial de Chat

**Antes:**
- Solo se mostraban los últimos 10 mensajes sin contexto adicional

**Después:**
- Análisis inteligente del contexto de conversación
- Filtrado de mensajes relevantes para viajes
- Extracción automática de información clave:
  - Destinos mencionados
  - Fechas mencionadas
  - Referencias a presupuesto
  - Actividades mencionadas

### 3. Configuración Optimizada del Modelo

**Antes:**
- Configuración genérica para todos los casos

**Después:**
- Configuraciones específicas por tipo de tarea:
  - `SEARCH_TEMPERATURE`: 0.1 (para búsquedas precisas)
  - `ITINERARY_TEMPERATURE`: 0.2 (para itinerarios consistentes)
  - `ITINERARY_MAX_TOKENS`: 12000 (para itinerarios detallados)
  - `SEARCH_MAX_TOKENS`: 4096 (para búsquedas)

### 4. Manejo Robusto de Errores

**Antes:**
- Manejo básico de errores

**Después:**
- Validación completa del contexto del viaje
- Validación de configuración de APIs
- Sugerencias específicas por tipo de error
- Logging detallado de actividades del agente

### 5. Integración con Servicios Externos

**Antes:**
- No había integración con APIs externas

**Después:**
- Integración con Amadeus API para búsqueda de vuelos y hoteles
- Búsqueda web simulada (preparada para integración real)
- Pronóstico del tiempo (preparado para integración real)

## Estructura de Datos Guardada

### Tabla `trips`
```sql
- id: UUID (PK)
- group_id: UUID (FK a groups)
- destination: VARCHAR
- start_date: DATE
- end_date: DATE
- status: BOOLEAN
```

### Tabla `itineraries`
```sql
- id: UUID (PK)
- trip_id: UUID (FK a trips)
- day: DATE
- activity: VARCHAR
- location: VARCHAR
- start_time: TIME
- end_time: TIME
- status: BOOLEAN
```

### Tabla `flights`
```sql
- id: UUID (PK)
- trip_id: UUID (FK a trips)
- airline: VARCHAR
- departure_airport: VARCHAR
- arrival_airport: VARCHAR
- departure_time: TIMESTAMP
- arrival_time: TIMESTAMP
- price: NUMERIC
- status: BOOLEAN
```

### Tabla `hotels`
```sql
- id: UUID (PK)
- trip_id: UUID (FK a trips)
- name: VARCHAR
- location: VARCHAR
- price_per_night: NUMERIC
- rating: NUMERIC
- link: VARCHAR
- status: BOOLEAN
```

## Endpoints Disponibles

### 1. Generar Itinerario
```
POST /ia_chat/send-message
```
Envía un mensaje al agente y genera un itinerario completo.

### 2. Obtener Itinerario Guardado
```
GET /ia_chat/itinerary/{group_id}
```
Obtiene el itinerario completo guardado para un grupo, incluyendo:
- Información del viaje
- Actividades del itinerario
- Vuelos recomendados
- Hoteles recomendados

## Configuración Requerida

### Variables de Entorno
```env
GROQ_API_KEY=tu_api_key_de_groq
AMADEUS_API_KEY=tu_api_key_de_amadeus
AMADEUS_API_SECRET=tu_api_secret_de_amadeus
```

### Configuraciones del Agente
```python
# Configuración para búsquedas
SEARCH_TEMPERATURE: 0.1
SEARCH_MAX_TOKENS: 4096

# Configuración para itinerarios
ITINERARY_TEMPERATURE: 0.2
ITINERARY_MAX_TOKENS: 12000

# Configuración de contexto
MAX_CHAT_HISTORY: 20
MAX_USER_CONTEXT: 5
```

## Flujo de Trabajo del Agente

1. **Recepción del Mensaje**: El usuario envía un mensaje al chat
2. **Validación**: Se valida el contexto y la configuración
3. **Análisis de Contexto**: Se analiza la conversación previa
4. **Búsqueda de Información**: Se usan herramientas para obtener datos actualizados
5. **Generación de Itinerario**: Se crea un itinerario personalizado
6. **Guardado en BD**: Se guardan todos los resultados en la base de datos
7. **Respuesta**: Se devuelve el itinerario al usuario

## Características del Itinerario Generado

- **Personalizado**: Basado en las preferencias de todos los participantes
- **Detallado**: Incluye actividades específicas con tiempos
- **Realista**: Incluye precios actualizados de vuelos y hoteles
- **Estructurado**: Respuesta en formato JSON para fácil procesamiento
- **Persistente**: Guardado en la base de datos para consulta posterior

## Logging y Debugging

El agente incluye logging detallado para debugging:
- Inicio de actividades
- Generación de prompts
- Llamadas a herramientas
- Resultados de búsquedas
- Guardado de itinerarios
- Errores y excepciones

## Próximos Pasos

1. **Integración de Búsqueda Web Real**: Conectar con APIs de búsqueda web
2. **Integración de Clima Real**: Conectar con APIs de pronóstico del tiempo
3. **Optimización de Prompts**: Mejorar los prompts para respuestas más específicas
4. **Interfaz de Usuario**: Crear una interfaz para visualizar itinerarios
5. **Notificaciones**: Implementar notificaciones cuando se genere un itinerario 