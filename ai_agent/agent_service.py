try:
    import groq
except ImportError:
    raise ImportError("Please install groq package with: pip install groq")

from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta
from .config import settings
from .models import TripContext, AgentResponse
from .travel_tools import TravelPriceSearcher

class TripPlannerAgent:
    def __init__(self):
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.price_searcher = TravelPriceSearcher(
            api_key=settings.AMADEUS_API_KEY,
            api_secret=settings.AMADEUS_API_SECRET
        )
        
    def _build_prompt(self, context: TripContext) -> str:
        """
        Construye el prompt para el agente de IA basado en el contexto del viaje
        """
        # Extraer información de los participantes
        participants_info = []
        for user in context.participants:
            user_info = f"Usuario {user.user_id}:\n"
            user_info += f"- Intereses: {', '.join(user.interests)}\n"
            if user.travel_preferences:
                user_info += f"- Preferencias de viaje: {user.travel_preferences}\n"
            if user.budget_preference:
                user_info += f"- Presupuesto: {user.budget_preference}\n"
            participants_info.append(user_info)
            
        chat_summary = "\n".join([
            f"{msg.user_id}: {msg.message}"
            for msg in context.chat_history[-10:]
        ])
        
        prompt = f"""Eres un experto planificador de viajes que ayuda a grupos a crear itinerarios personalizados.
        
CONTEXTO DEL GRUPO:
{'\n'.join(participants_info)}

CONVERSACIÓN RECIENTE DEL GRUPO:
{chat_summary}

{context.specific_requirements or 'Por favor, genera un itinerario detallado considerando los intereses y preferencias del grupo.'}

HERRAMIENTAS DISPONIBLES:
1. search_web: Busca información actualizada sobre destinos, atracciones, hoteles y vuelos
2. get_weather: Obtiene el pronóstico del tiempo para una ubicación
3. get_prices: Obtiene precios actualizados de hoteles y vuelos

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
        
    def _process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Procesa las llamadas a herramientas del modelo
        """
        results = {}
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            arguments = json.loads(tool_call.get("arguments", "{}"))
            
            if tool_name == "get_prices":
                try:
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
                        flights = self.price_searcher.search_flights(
                            origin=origin,
                            destination=destination,
                            departure_date=check_in,
                            return_date=check_out if len(dates) > 1 else None
                        )
                        results[f"flights_{origin}_{destination}"] = self.price_searcher.format_results_for_agent(flights=flights)
                        
                    elif search_type == "hotel":
                        hotels = self.price_searcher.search_hotels(
                            city=location,
                            check_in=check_in,
                            check_out=check_out,  # Ahora siempre pasamos una fecha válida
                            guests=2  # Valor por defecto
                        )
                        results[f"hotels_{location}"] = self.price_searcher.format_results_for_agent(hotels=hotels)
                        
                except Exception as e:
                    results[f"error_{tool_name}"] = str(e)
                    
            elif tool_name == "search_web":
                # Implementar lógica de búsqueda web
                pass
            elif tool_name == "get_weather":
                # Implementar lógica de pronóstico del tiempo
                pass
                
        return results
        
    def generate_itinerary(self, context: TripContext) -> AgentResponse:
        """
        Genera un itinerario basado en el contexto del viaje
        """
        try:
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
                    }
                ]
            )
            
            # Procesar la respuesta y las llamadas a herramientas
            response = completion.choices[0].message
            
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Procesar las llamadas a herramientas y obtener resultados
                tool_results = self._process_tool_calls(response.tool_calls)
                
                # Segunda llamada incluyendo los resultados de las búsquedas
                final_prompt = f"""Basado en las búsquedas realizadas, aquí están los resultados:

{json.dumps(tool_results, indent=2, ensure_ascii=False)}

Por favor, genera un itinerario final que incorpore estas opciones de vuelos y hoteles,
asegurándote de seleccionar las mejores opciones según el presupuesto y preferencias del grupo.
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
                    reasoning="Itinerario generado basado en precios reales y preferencias del grupo"
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