try:
    import groq
except ImportError:
    raise ImportError("Please install groq package with: pip install groq")

from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .models import TripContext, AgentResponse, ChatMessage, UserPreferences
from .travel_tools import TravelPriceSearcher
from .travel_service import TravelService
from .chat_service_sync import ChatServiceSync

class TripPlannerAgent:
    def __init__(self, db: AsyncSession):
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.travel_service = TravelService(
            db=db,
            api_key=settings.AMADEUS_API_KEY,
            api_secret=settings.AMADEUS_API_SECRET
        )
        self.chat_service = ChatServiceSync(db=db)
        self.db = db
        
    async def _build_prompt(self, context: TripContext) -> str:
        """
        Construye el prompt para el agente de IA basado en el contexto del viaje y el historial
        """
        # Obtener el contexto del grupo
        group_context = await self.chat_service.get_group_context(context.group_id)
        
        # Extraer información de los participantes
        participants_info = []
        # Crear un diccionario para mapear user_id a nombres
        user_names = {str(user.user_id): user.name for user in context.participants}
        
        for user in context.participants:
            # Obtener el contexto del usuario
            user_context = await self.chat_service.get_user_context(user.user_id)
            
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
        
    async def _process_tool_calls(self, tool_calls: List[Any], trip_id: uuid.UUID) -> Dict[str, Any]:
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
                        try:
                            # Asumimos que location tiene formato "ORIGEN-DESTINATION"
                            origin, destination = location.split("-")
                            # Limpiar resultados anteriores
                            await self.travel_service.clear_trip_results(trip_id)
                            # Buscar y guardar nuevos resultados
                            flights = await self.travel_service.search_and_save_flights(
                                trip_id=trip_id,
                                origin=origin,
                                destination=destination,
                                departure_date=check_in,
                                return_date=check_out if len(dates) > 1 else None
                            )
                            results[f"flights_{origin}_{destination}"] = await self.travel_service.format_saved_results(flights=flights)
                        except Exception as e:
                            # Si hay error con Amadeus, lanzar el error
                            print(f"Error con Amadeus para vuelos: {e}")
                            raise e
                        
                    elif search_type == "hotel":
                        try:
                            # Limpiar resultados anteriores
                            await self.travel_service.clear_trip_results(trip_id)
                            # Buscar y guardar nuevos resultados
                            hotels = await self.travel_service.search_and_save_hotels(
                                trip_id=trip_id,
                                city=location,
                                check_in=check_in,
                                check_out=check_out,
                                guests=2  # Valor por defecto
                            )
                            results[f"hotels_{location}"] = await self.travel_service.format_saved_results(hotels=hotels)
                        except Exception as e:
                            # Si hay error con Amadeus, lanzar el error
                            print(f"Error con Amadeus para hoteles: {e}")
                            raise e
                        
                # Eliminar bloques para search_web y get_weather
                # elif tool_name == "search_web":
                #     query = arguments.get("query")
                #     if not query:
                #         raise ValueError("Se requiere una consulta para la búsqueda web")
                #     results[f"web_search_{query[:30]}"] = await self.search_web(query)
                    
                # elif tool_name == "get_weather":
                #     location = arguments.get("location")
                #     dates = arguments.get("dates", [])
                #     if not location:
                #         raise ValueError("Se requiere una ubicación para el pronóstico")
                #     results[f"weather_{location}"] = await self.get_weather(location, dates)
                    
            except Exception as e:
                print(f"Error en herramienta {tool_name}: {e}")
                results[f"error_{tool_name}"] = await self._handle_tool_error(tool_name, e)
                
        return results
        
    async def generate_itinerary(self, context: TripContext, trip_id: uuid.UUID) -> AgentResponse:
        """
        Genera un itinerario basado en el contexto del viaje
        """
        try:
            # Validar el contexto antes de procesar
            await self._validate_trip_context(context)
            
            prompt = await self._build_prompt(context)
            
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
                tool_results = await self._process_tool_calls(response.tool_calls, trip_id)
                
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
                    itinerary=final_completion.choices[0].message.content or "",
                    reasoning="Itinerario generado basado en precios reales, clima y preferencias del grupo"
                )
            
            return AgentResponse(
                itinerary=response.content or "",
                reasoning="Itinerario generado basado en preferencias del grupo"
            )
            
        except Exception as e:
            return AgentResponse(
                itinerary="",
                error=f"Error generando el itinerario: {str(e)}"
            )

    # Eliminar search_web y get_weather simulados
    # El agente ahora solo usa Groq compound-beta para obtener información real

    # Puedes dejar funciones utilitarias si son necesarias, pero no datos simulados

    async def _handle_tool_error(self, tool_name: str, error: Exception) -> Dict[str, str]:
        """Maneja errores de las herramientas de forma consistente"""
        error_response = {
            "error": str(error),
            "tool": tool_name,
            "timestamp": datetime.now().isoformat()
        }
        return error_response

    async def _validate_trip_context(self, context: TripContext) -> None:
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

    async def process_message(self, context: TripContext, trip_id: uuid.UUID) -> str:
        """
        Procesa un mensaje del usuario y genera una respuesta usando el modelo agentic tooling de Groq (compound-beta),
        usando el contexto y preferencias del grupo y participantes.
        """
        try:
            await self._validate_trip_context(context)
            user_message = context.specific_requirements or "Ayúdame a planificar mi viaje"
            requiere_itinerario = any(word in user_message.lower() for word in ["itinerario", "plan", "agenda", "actividades"])
            prompt = f"""Eres un experto asistente de viajes. Un usuario te ha enviado este mensaje:

\"{user_message}\"

CONTEXTO DEL GRUPO:
Grupo ID: {context.group_id}

INFORMACIÓN DE PARTICIPANTES:
{chr(10).join([f"- {p.name}: {', '.join(p.destinations)} destinos, {', '.join(p.activities)} actividades" for p in context.participants])}

HISTORIAL RECIENTE:
{chr(10).join([f"{msg.user_id}: {msg.message}" for msg in context.chat_history[-5:]])}

Por favor, busca en la web vuelos y hoteles reales si es necesario, y responde con la información más actualizada y útil posible."""
            if requiere_itinerario:
                prompt += "\n\nEl usuario ha solicitado un itinerario. Genera un itinerario diario detallado para el viaje, incluyendo actividades recomendadas (por ejemplo, rutas de hiking, visitas a parques naturales, excursiones), lugares para comer (restaurantes locales, comida típica), y cualquier recomendación relevante para el destino y las fechas. Responde en formato JSON estructurado, por ejemplo:\n\n{\n  \"itinerary_days\": [\n    {\n      \"day\": 1,\n      \"activities\": [\n        {\n          \"activity\": \"Hiking en el Parque Nacional XYZ\",\n          \"location\": \"Parque Nacional XYZ\",\n          \"time\": \"09:00\"\n        },\n        {\n          \"activity\": \"Almuerzo en Restaurante ABC\",\n          \"location\": \"Restaurante ABC\",\n          \"time\": \"13:00\"\n        }\n      ]\n    },\n    ...\n  ]\n}\n\nIncluye actividades de hiking y recomendaciones gastronómicas locales."
            else:
                prompt += "\n\nSi el usuario solicita un itinerario, responde en formato JSON estructurado."
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un experto asistente de viajes que puede buscar en la web en tiempo real usando agentic tooling."},
                    {"role": "user", "content": prompt}
                ],
                model="compound-beta",
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS
            )
            response = completion.choices[0].message
            return response.content or ""
        except Exception as e:
            return f"Lo siento, hubo un error procesando tu mensaje: {str(e)}"

    async def _process_itinerary_response(self, response: str, trip_id: uuid.UUID) -> None:
        """
        Procesa la respuesta del agente para extraer y guardar itinerarios si están en formato JSON
        """
        try:
            # Intentar parsear como JSON
            import json
            from datetime import datetime, date
            from app.models.itinerary import Itinerary
            
            # Buscar JSON en la respuesta (puede estar mezclado con texto)
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                data = json.loads(json_str)
                
                # Verificar si es un itinerario
                if 'itinerary_days' in data:
                    # Limpiar itinerarios anteriores
                    from sqlalchemy import update
                    stmt = update(Itinerary).where(Itinerary.trip_id == trip_id).values(status=False)
                    await self.db.execute(stmt)
                    
                    # Guardar nuevos itinerarios
                    for day_data in data['itinerary_days']:
                        day_num = day_data.get('day', 1)
                        activities = day_data.get('activities', [])
                        
                        for activity in activities:
                            # Calcular fecha basada en el día
                            # Por ahora usamos la fecha actual + días
                            activity_date = date.today() + timedelta(days=day_num - 1)
                            
                            # Parsear tiempo
                            time_str = activity.get('time', '09:00')
                            try:
                                start_time = datetime.strptime(time_str, '%H:%M').time()
                                # Asumir 2 horas por actividad
                                end_time = datetime.strptime(time_str, '%H:%M').replace(hour=(int(time_str[:2]) + 2) % 24).time()
                            except:
                                start_time = None
                                end_time = None
                            
                            itinerary = Itinerary(
                                trip_id=trip_id,
                                day=activity_date,
                                activity=activity.get('activity', ''),
                                location=activity.get('location', ''),
                                start_time=start_time,
                                end_time=end_time,
                                status=True
                            )
                            self.db.add(itinerary)
                    
                    await self.db.commit()
                    
        except Exception as e:
            # Si no es JSON válido o no es un itinerario, simplemente continuar
            pass

    async def save_agent_response(self, group_id: uuid.UUID, response: str) -> None:
        """
        Guarda la respuesta del agente en el historial de chat
        """
        await self.chat_service.save_message(
            user_id=settings.AGENT_USER_ID,  # ID especial para el agente
            group_id=group_id,
            message=response
        ) 