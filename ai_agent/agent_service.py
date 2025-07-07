try:
    import groq
except ImportError:
    raise ImportError("Please install groq package with: pip install groq")

from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .config import settings
from .models import TripContext, AgentResponse, ChatMessage, UserPreferences
from .travel_tools import TravelPriceSearcher
from .travel_service import TravelService
from app.services.chat_service import ChatService
from app.models.trip import Trip
from app.models.itinerary import Itinerary

class TripPlannerAgent:
    def __init__(self, db: Session):
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.travel_service = TravelService(
            db=db,
            api_key=settings.AMADEUS_API_KEY,
            api_secret=settings.AMADEUS_API_SECRET
        )
        self.chat_service = ChatService(db=db)
        self.db = db
        
    def _build_prompt(self, context: TripContext) -> str:
        """
        Construye el prompt para el agente de IA basado en el contexto del viaje y el historial
        """
        # Obtener el contexto del grupo
        group_context = self.chat_service.get_group_context(context.group_id)
        
        # Extraer información de los participantes
        participants_info = []
        # Crear un diccionario para mapear user_id a nombres
        user_names = {str(user.user_id): user.name for user in context.participants}
        
        for user in context.participants:
            # Obtener el contexto del usuario
            user_context = self.chat_service.get_user_context(user.user_id)
            
            user_info = f"Usuario {user.name} ({user.user_id}):\n"
            user_info += f"- Destinos preferidos: {', '.join(user.destinations)}\n"
            user_info += f"- Actividades: {', '.join(user.activities)}\n"
            user_info += f"- Presupuesto: {', '.join(user.prices)}\n"
            user_info += f"- Alojamientos: {', '.join(user.accommodations)}\n"
            user_info += f"- Transportes: {', '.join(user.transport)}\n"
            user_info += f"- Motivaciones: {', '.join(user.motivations)}\n"
            
            # Agregar información del contexto del usuario si existe
            if user_context:
                recent_interactions = user_context.get("recent_interactions", [])
                if recent_interactions:
                    user_info += "- Interacciones recientes:\n"
                    for interaction in recent_interactions[:3]:  # Solo las 3 más recientes
                        user_info += f"  * {interaction['message']}\n"
                        
            participants_info.append(user_info)
            
        # Obtener los últimos mensajes del grupo con más contexto
        recent_messages = group_context.get("recent_messages", [])
        
        # Filtrar mensajes relevantes para el viaje (últimos 20 en lugar de 10)
        relevant_messages = []
        for msg in recent_messages[:20]:
            message_text = msg.get('message', '').lower()
            # Incluir mensajes que contengan palabras clave relacionadas con viajes
            travel_keywords = ['viaje', 'destino', 'hotel', 'vuelo', 'actividad', 'plan', 'itinerario', 
                             'fecha', 'presupuesto', 'lugar', 'visitar', 'explorar', 'turismo']
            if any(keyword in message_text for keyword in travel_keywords) or len(message_text) > 10:
                relevant_messages.append(msg)
        
        # Si no hay mensajes relevantes, incluir los últimos 5 mensajes
        if not relevant_messages and recent_messages:
            relevant_messages = recent_messages[:5]
        
        chat_summary = "\n".join([
            f"{user_names.get(msg['user_id'], msg['user_id'])}: {msg['message']}"
            for msg in relevant_messages
        ])
        
        # Agregar análisis del contexto de la conversación
        conversation_analysis = self._analyze_conversation_context(relevant_messages)
        
        prompt = f"""Eres un experto planificador de viajes que ayuda a grupos a crear itinerarios personalizados.
        
CONTEXTO DEL GRUPO:
Grupo: {group_context.get('group', {}).get('name', 'Sin nombre')}

INFORMACIÓN DE PARTICIPANTES:
{'\n'.join(participants_info)}

ANÁLISIS DE LA CONVERSACIÓN:
{conversation_analysis}

CONVERSACIÓN RECIENTE DEL GRUPO:
{chat_summary}

REQUERIMIENTO ESPECÍFICO:
{context.specific_requirements or 'Por favor, genera un itinerario detallado considerando los intereses y preferencias del grupo, así como la conversación reciente del grupo.'}

HERRAMIENTAS DISPONIBLES:
1. search_web: Busca información actualizada sobre destinos, atracciones, hoteles y vuelos
2. get_weather: Obtiene el pronóstico del tiempo para una ubicación
3. get_prices: Obtiene precios actualizados de hoteles o vuelos

Tu tarea es:
1. Analizar los intereses y preferencias de cada participante
2. Usar las herramientas disponibles para obtener información actualizada
3. Crear un itinerario detallado que:
   - Balance los intereses de todos los participantes
   - Incluya actividades específicas con tiempos
   - Considere logística y tiempos de traslado
   - Sugiera opciones de alojamiento y transporte basadas en búsquedas reales
   - Proporcione estimaciones de costos actualizadas
   
Por favor, estructura tu respuesta en formato JSON con los siguientes campos:
{
    "itinerary_days": [
        {
            "day": 1,
            "activities": [
                {
                    "time": "string",
                    "activity": "string",
                    "location": "string",
                    "estimated_cost": "string",
                    "notes": "string"
                }
            ]
        }
    ],
    "total_estimated_cost": "string",
    "recommendations": ["string"],
    "weather_considerations": "string",
    "destination": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
}"""

        return prompt
        
    def _process_tool_calls(self, tool_calls: List[Any], trip_id: uuid.UUID) -> Dict[str, Any]:
        """
        Procesa las llamadas a herramientas del modelo
        """
        results = {}
        for tool_call in tool_calls:
            # Convert ChoiceMessageToolCall to Dict if needed
            if not isinstance(tool_call, dict):
                tool_call = {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            
            tool_name = str(tool_call.get("name", "unknown_tool"))
            arguments = json.loads(tool_call.get("arguments", "{}"))
            
            try:
                if tool_name == "get_prices":
                    search_type = arguments.get("type")
                    location = arguments.get("location")
                    dates = arguments.get("dates", "").split(",")
                    
                    # Asegurarnos de tener al menos una fecha
                    if not dates or not dates[0].strip():
                        raise ValueError("Se requiere al menos una fecha")
                        
                    check_in = dates[0].strip()
                    
                    # Si no hay fecha de salida, asumimos el día siguiente
                    if len(dates) > 1 and dates[1].strip():
                        check_out = dates[1].strip()
                    else:
                        check_out_date = datetime.strptime(check_in, "%Y-%m-%d") + timedelta(days=1)
                        check_out = check_out_date.strftime("%Y-%m-%d")
                    
                    if search_type == "flight":
                        # Asumimos que location tiene formato "ORIGIN-DESTINATION"
                        origin, destination = location.split("-")
                        # Limpiar resultados anteriores
                        self.travel_service.clear_trip_results(trip_id)
                        # Buscar y guardar nuevos resultados
                        flights = self.travel_service.search_and_save_flights(
                            trip_id=trip_id,
                            origin=origin,
                            destination=destination,
                            departure_date=check_in,
                            return_date=check_out if len(dates) > 1 else None
                        )
                        results[f"flights_{origin}_{destination}"] = self.travel_service.format_saved_results(flights=flights)
                        
                    elif search_type == "hotel":
                        # Limpiar resultados anteriores
                        self.travel_service.clear_trip_results(trip_id)
                        # Buscar y guardar nuevos resultados
                        hotels = self.travel_service.search_and_save_hotels(
                            trip_id=trip_id,
                            city=location,
                            check_in=check_in,
                            check_out=check_out,
                            guests=2  # Valor por defecto
                        )
                        results[f"hotels_{location}"] = self.travel_service.format_saved_results(hotels=hotels)
                        
                elif tool_name == "search_web":
                    query = arguments.get("query")
                    if not query:
                        raise ValueError("Se requiere una consulta para la búsqueda web")
                    results[f"web_search_{query[:30]}"] = self.search_web(query)
                    
                elif tool_name == "get_weather":
                    location = arguments.get("location")
                    dates = arguments.get("dates", [])
                    if not location:
                        raise ValueError("Se requiere una ubicación para el pronóstico")
                    results[f"weather_{location}"] = self.get_weather(location, dates)
                    
            except Exception as e:
                results[f"error_{tool_name}"] = self._handle_tool_error(tool_name, e)
                
        return results

    def _save_itinerary_to_database(self, trip_id: uuid.UUID, itinerary_data: Dict[str, Any]) -> None:
        """
        Guarda el itinerario generado en la base de datos
        """
        try:
            # Actualizar información del viaje
            trip = self.db.query(Trip).filter(Trip.id == trip_id).first()
            if trip:
                trip.destination = itinerary_data.get("destination", "")
                trip.start_date = datetime.strptime(itinerary_data.get("start_date", ""), "%Y-%m-%d").date() if itinerary_data.get("start_date") else None
                trip.end_date = datetime.strptime(itinerary_data.get("end_date", ""), "%Y-%m-%d").date() if itinerary_data.get("end_date") else None
                
            # Guardar actividades del itinerario
            itinerary_days = itinerary_data.get("itinerary_days", [])
            for day_data in itinerary_days:
                day_number = day_data.get("day", 1)
                activities = day_data.get("activities", [])
                
                for activity in activities:
                    # Calcular la fecha del día
                    if trip and trip.start_date:
                        activity_date = trip.start_date + timedelta(days=day_number - 1)
                    else:
                        activity_date = datetime.now().date()
                    
                    # Parsear tiempo de inicio y fin
                    time_str = activity.get("time", "")
                    start_time = None
                    end_time = None
                    
                    if "-" in time_str:
                        times = time_str.split("-")
                        if len(times) == 2:
                            start_time = datetime.strptime(times[0].strip(), "%H:%M").time()
                            end_time = datetime.strptime(times[1].strip(), "%H:%M").time()
                    
                    # Crear entrada del itinerario
                    itinerary_entry = Itinerary(
                        trip_id=trip_id,
                        day=activity_date,
                        activity=activity.get("activity", ""),
                        location=activity.get("location", ""),
                        start_time=start_time,
                        end_time=end_time,
                        status=True
                    )
                    self.db.add(itinerary_entry)
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            print(f"Error guardando itinerario en base de datos: {str(e)}")
            raise
        
    def generate_itinerary(self, context: TripContext, trip_id: uuid.UUID) -> AgentResponse:
        """
        Genera un itinerario basado en el contexto del viaje
        """
        try:
            # Log de inicio de actividad
            self._log_agent_activity("generate_itinerary_start", {
                "trip_id": str(trip_id),
                "group_id": str(context.group_id),
                "participants_count": len(context.participants)
            })
            
            # Validar configuración de APIs
            self._validate_api_configuration()
            
            # Validar el contexto antes de procesar
            self._validate_trip_context(context)
            
            prompt = self._build_prompt(context)
            
            # Log del prompt generado
            self._log_agent_activity("prompt_generated", {
                "prompt_length": len(prompt),
                "has_tools": True
            })
            
            # Primera llamada para obtener los requisitos de búsqueda
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un experto planificador de viajes que ayuda a grupos."},
                    {"role": "user", "content": prompt}
                ],
                model=settings.MODEL_NAME,
                temperature=settings.SEARCH_TEMPERATURE,  # Usar temperatura de búsqueda
                max_tokens=settings.SEARCH_MAX_TOKENS,   # Usar tokens de búsqueda
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_prices",
                            "description": "Obtiene precios actualizados de hoteles o vuelos",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["hotel", "flight"]},
                                    "location": {"type": "string", "description": "Para vuelos: 'ORIGEN-DESTINO' (códigos IATA). Para hoteles: código de ciudad"},
                                    "dates": {"type": "string", "description": "Fechas en formato 'YYYY-MM-DD' separadas por coma"}
                                },
                                "required": ["type", "location", "dates"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "search_web",
                            "description": "Busca información actualizada sobre destinos y atracciones",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Consulta de búsqueda"}
                                },
                                "required": ["query"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "description": "Obtiene el pronóstico del tiempo para una ubicación",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {"type": "string", "description": "Nombre de la ciudad o ubicación"},
                                    "dates": {"type": "array", "items": {"type": "string"}, "description": "Lista de fechas en formato YYYY-MM-DD"}
                                },
                                "required": ["location"]
                            }
                        }
                    }
                ]
            )
            
            # Procesar la respuesta y las llamadas a herramientas
            response = completion.choices[0].message
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Log de llamadas a herramientas
                self._log_agent_activity("tool_calls_detected", {
                    "tool_calls_count": len(response.tool_calls),
                    "tools": [tc.get("name", "unknown") for tc in response.tool_calls]
                })
                
                # Procesar las llamadas a herramientas y obtener resultados
                tool_results = self._process_tool_calls(response.tool_calls, trip_id)
                
                # Log de resultados de herramientas
                self._log_agent_activity("tool_results_processed", {
                    "results_count": len(tool_results),
                    "has_errors": any("error_" in key for key in tool_results.keys())
                })
                
                # Segunda llamada incluyendo los resultados de las búsquedas
                final_prompt = f"""Basado en las búsquedas realizadas, aquí están los resultados:

{json.dumps(tool_results, indent=2, ensure_ascii=False)}

Por favor, genera un itinerario final que incorpore esta información,
asegurándote de seleccionar las mejores opciones según el presupuesto y preferencias del grupo.
Incluye recomendaciones específicas basadas en el clima y la información de los destinos.
"""
                
                final_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres un experto planificador de viajes que ayuda a grupos."},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": response.content},
                        {"role": "user", "content": final_prompt}
                    ],
                    model=settings.MODEL_NAME,
                    temperature=settings.ITINERARY_TEMPERATURE,  # Usar temperatura específica para itinerarios
                    max_tokens=settings.ITINERARY_MAX_TOKENS,    # Usar tokens específicos para itinerarios
                    response_format={"type": "json_object"}  # Forzar respuesta JSON
                )
                
                final_response = final_completion.choices[0].message.content
                
                # Intentar parsear la respuesta como JSON para guardar en BD
                try:
                    itinerary_data = json.loads(final_response)
                    self._save_itinerary_to_database(trip_id, itinerary_data)
                    
                    # Log de itinerario guardado
                    self._log_agent_activity("itinerary_saved", {
                        "trip_id": str(trip_id),
                        "days_count": len(itinerary_data.get("itinerary_days", [])),
                        "destination": itinerary_data.get("destination", "")
                    })
                    
                except json.JSONDecodeError as e:
                    # Log de error de parsing JSON
                    self._log_agent_activity("json_parse_error", {
                        "error": str(e),
                        "response_preview": final_response[:200]
                    })
                
                return AgentResponse(
                    itinerary=final_response,
                    reasoning="Itinerario generado basado en precios reales, clima y preferencias del grupo"
                )
            
            # Si no hay llamadas a herramientas, generar itinerario directo
            self._log_agent_activity("no_tool_calls", {
                "message": "Generando itinerario sin búsquedas externas"
            })
            
            direct_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un experto planificador de viajes que ayuda a grupos."},
                    {"role": "user", "content": prompt}
                ],
                model=settings.MODEL_NAME,
                temperature=settings.ITINERARY_TEMPERATURE,
                max_tokens=settings.ITINERARY_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            direct_response = direct_completion.choices[0].message.content
            
            # Intentar parsear la respuesta como JSON para guardar en BD
            try:
                itinerary_data = json.loads(direct_response)
                self._save_itinerary_to_database(trip_id, itinerary_data)
                
                # Log de itinerario guardado
                self._log_agent_activity("itinerary_saved", {
                    "trip_id": str(trip_id),
                    "days_count": len(itinerary_data.get("itinerary_days", [])),
                    "destination": itinerary_data.get("destination", "")
                })
                
            except json.JSONDecodeError as e:
                # Log de error de parsing JSON
                self._log_agent_activity("json_parse_error", {
                    "error": str(e),
                    "response_preview": direct_response[:200]
                })
            
            return AgentResponse(
                itinerary=direct_response,
                reasoning="Itinerario generado basado en preferencias del grupo"
            )
            
        except Exception as e:
            # Log de error
            self._log_agent_activity("error", {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "trip_id": str(trip_id)
            })
            
            return AgentResponse(
                itinerary="",
                error=f"Error generando el itinerario: {str(e)}"
            )

    def search_web(self, query: str) -> Dict[str, Any]:
        """Busca información actualizada sobre destinos y atracciones"""
        try:
            # Usar la herramienta web_search para obtener información actualizada
            search_results = {
                "query": query,
                "results": "Función simulada: Aquí se integraría la búsqueda web real",
                "timestamp": datetime.now().isoformat()
            }
            
            return search_results
            
        except Exception as e:
            return self._handle_tool_error("search_web", e)

    def get_weather(self, location: str, dates: List[str]) -> Dict[str, Any]:
        """Obtiene el pronóstico del tiempo para una ubicación"""
        try:
            # Construir la consulta para el clima
            weather_info = {
                "location": location,
                "dates": dates,
                "forecast": "Función simulada: Aquí se integraría el pronóstico real",
                "timestamp": datetime.now().isoformat()
            }
            
            return weather_info
            
        except Exception as e:
            return self._handle_tool_error("get_weather", e)

    def _handle_tool_error(self, tool_name: str, error: Exception) -> Dict[str, str]:
        """Maneja errores de las herramientas de forma consistente"""
        error_response = {
            "error": str(error),
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "suggestion": self._get_error_suggestion(tool_name, error)
        }
        return error_response

    def _get_error_suggestion(self, tool_name: str, error: Exception) -> str:
        """Proporciona sugerencias específicas para diferentes tipos de errores"""
        error_msg = str(error).lower()
        
        if tool_name == "get_prices":
            if "api" in error_msg or "key" in error_msg:
                return "Verificar configuración de API de Amadeus"
            elif "date" in error_msg or "fecha" in error_msg:
                return "Verificar formato de fechas (YYYY-MM-DD)"
            elif "location" in error_msg or "ubicación" in error_msg:
                return "Verificar códigos de aeropuerto/ciudad válidos"
            else:
                return "Verificar parámetros de búsqueda"
        
        elif tool_name == "search_web":
            if "network" in error_msg or "connection" in error_msg:
                return "Verificar conexión a internet"
            else:
                return "Verificar consulta de búsqueda"
        
        elif tool_name == "get_weather":
            if "location" in error_msg:
                return "Verificar nombre de ubicación válido"
            else:
                return "Verificar parámetros de clima"
        
        return "Revisar configuración y parámetros"

    def _validate_trip_context(self, context: TripContext) -> None:
        """Valida que el contexto del viaje tenga toda la información necesaria"""
        errors = []
        
        if not context.participants:
            errors.append("El contexto debe tener al menos un participante")
        
        if not context.group_id:
            errors.append("El contexto debe tener un group_id válido")
        
        for i, participant in enumerate(context.participants):
            if not participant.user_id:
                errors.append(f"Participante {i+1}: Falta user_id")
            
            if not participant.name:
                errors.append(f"Participante {i+1}: Falta nombre")
            
            # Validar que tenga al menos algunas preferencias
            has_preferences = any([
                participant.destinations,
                participant.activities,
                participant.prices,
                participant.accommodations,
                participant.transport,
                participant.motivations
            ])
            
            if not has_preferences:
                errors.append(f"Participante {participant.name}: No tiene preferencias definidas")
        
        if errors:
            raise ValueError(f"Errores de validación: {'; '.join(errors)}")

    def _validate_api_configuration(self) -> None:
        """Valida que la configuración de APIs esté correcta"""
        errors = []
        
        if not settings.GROQ_API_KEY:
            errors.append("GROQ_API_KEY no está configurada")
        
        if settings.ENABLE_FLIGHT_SEARCH or settings.ENABLE_HOTEL_SEARCH:
            if not settings.AMADEUS_API_KEY:
                errors.append("AMADEUS_API_KEY no está configurada para búsquedas de vuelos/hoteles")
            
            if not settings.AMADEUS_API_SECRET:
                errors.append("AMADEUS_API_SECRET no está configurada para búsquedas de vuelos/hoteles")
        
        if errors:
            raise ValueError(f"Errores de configuración: {'; '.join(errors)}")

    def _log_agent_activity(self, action: str, details: Dict[str, Any]) -> None:
        """Registra la actividad del agente para debugging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        print(f"=== AGENT LOG ===\n{json.dumps(log_entry, indent=2)}\n================")

    def save_agent_response(self, group_id: uuid.UUID, response: str) -> None:
        """
        Guarda la respuesta del agente en el historial de chat
        """
        self.chat_service.save_message(
            user_id=settings.AGENT_USER_ID,  # ID especial para el agente
            group_id=group_id,
            message=response
        )

    def _analyze_conversation_context(self, messages: List[Dict[str, Any]]) -> str:
        """
        Analiza el contexto de la conversación para extraer información relevante
        """
        if not messages:
            return "No hay conversación previa registrada."
        
        # Extraer información clave de los mensajes
        destinations_mentioned = []
        dates_mentioned = []
        budget_mentioned = []
        activities_mentioned = []
        
        for msg in messages:
            message_text = msg.get('message', '').lower()
            
            # Buscar destinos mencionados
            destination_keywords = ['quiero ir a', 'me gustaría visitar', 'destino', 'lugar', 'ciudad']
            if any(keyword in message_text for keyword in destination_keywords):
                # Extraer el nombre del destino (simplificado)
                destinations_mentioned.append(message_text)
            
            # Buscar fechas mencionadas
            import re
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
                r'\d{4}-\d{2}-\d{2}',       # YYYY-MM-DD
                r'\d{1,2}-\d{1,2}-\d{4}',   # DD-MM-YYYY
            ]
            for pattern in date_patterns:
                dates = re.findall(pattern, message_text)
                dates_mentioned.extend(dates)
            
            # Buscar presupuesto mencionado
            budget_keywords = ['presupuesto', 'costo', 'precio', 'gastar', 'dólares', 'euros', 'pesos']
            if any(keyword in message_text for keyword in budget_keywords):
                budget_mentioned.append(message_text)
            
            # Buscar actividades mencionadas
            activity_keywords = ['actividad', 'visitar', 'explorar', 'hacer', 'ver', 'conocer']
            if any(keyword in message_text for keyword in activity_keywords):
                activities_mentioned.append(message_text)
        
        analysis = "INFORMACIÓN EXTRAÍDA DE LA CONVERSACIÓN:\n"
        
        if destinations_mentioned:
            analysis += f"- Destinos mencionados: {', '.join(destinations_mentioned[:3])}\n"
        
        if dates_mentioned:
            analysis += f"- Fechas mencionadas: {', '.join(list(set(dates_mentioned)))}\n"
        
        if budget_mentioned:
            analysis += f"- Referencias a presupuesto: {', '.join(budget_mentioned[:2])}\n"
        
        if activities_mentioned:
            analysis += f"- Actividades mencionadas: {', '.join(activities_mentioned[:3])}\n"
        
        if not any([destinations_mentioned, dates_mentioned, budget_mentioned, activities_mentioned]):
            analysis += "- No se detectó información específica de viaje en la conversación.\n"
        
        return analysis 