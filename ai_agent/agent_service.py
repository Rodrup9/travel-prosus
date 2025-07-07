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
            
        # Obtener los últimos mensajes del grupo
        recent_messages = group_context.get("recent_messages", [])
        chat_summary = "\n".join([
            f"{user_names.get(msg['user_id'], msg['user_id'])}: {msg['message']}"
            for msg in recent_messages
        ])
        
        prompt = f"""Eres un experto planificador de viajes que ayuda a grupos a crear itinerarios personalizados.
        
CONTEXTO DEL GRUPO:
Grupo: {group_context.get('group', {}).get('name', 'Sin nombre')}

INFORMACIÓN DE PARTICIPANTES:
{'\n'.join(participants_info)}

CONVERSACIÓN RECIENTE DEL GRUPO:
{chat_summary}

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
    "weather_considerations": "string"
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
        
    def generate_itinerary(self, context: TripContext, trip_id: uuid.UUID) -> AgentResponse:
        """
        Genera un itinerario basado en el contexto del viaje
        """
        try:
            # Validar el contexto antes de procesar
            self._validate_trip_context(context)
            
            prompt = self._build_prompt(context)
            
            # Primera llamada para obtener los requisitos de búsqueda
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un experto planificador de viajes que ayuda a grupos."},
                    {"role": "user", "content": prompt}
                ],
                model=settings.MODEL_NAME,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
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
                # Procesar las llamadas a herramientas y obtener resultados
                tool_results = self._process_tool_calls(response.tool_calls, trip_id)
                
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
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                
                return AgentResponse(
                    itinerary=final_completion.choices[0].message.content,
                    reasoning="Itinerario generado basado en precios reales, clima y preferencias del grupo"
                )
            
            return AgentResponse(
                itinerary=response.content,
                reasoning="Itinerario generado basado en preferencias del grupo"
            )
            
        except Exception as e:
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
            "timestamp": datetime.now().isoformat()
        }
        return error_response

    def _validate_trip_context(self, context: TripContext) -> None:
        """Valida que el contexto del viaje tenga toda la información necesaria"""
        if not context.participants:
            raise ValueError("El contexto debe tener al menos un participante")
            
        for participant in context.participants:
            if not participant.user_id or not participant.name:
                raise ValueError("Todos los participantes deben tener ID y nombre")
            if not any([participant.destinations, participant.activities, 
                       participant.prices, participant.accommodations,
                       participant.transport, participant.motivations]):
                raise ValueError(f"El participante {participant.name} no tiene preferencias definidas")

    def save_agent_response(self, group_id: uuid.UUID, response: str) -> None:
        """
        Guarda la respuesta del agente en el historial de chat
        """
        self.chat_service.save_message(
            user_id=settings.AGENT_USER_ID,  # ID especial para el agente
            group_id=group_id,
            message=response
        ) 