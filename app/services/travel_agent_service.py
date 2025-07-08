from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from ai_agent.agent_service import TripPlannerAgent
from ai_agent.models import TripContext, UserPreferences
from app.models.ia_chat import IAChat
from app.models.user import User
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.trip import Trip
from app.models.flight import Flight
from app.models.hotel import Hotel
from app.models.itinerary import Itinerary
from app.services.chat_service import ChatService
import json

class TravelAgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def _get_sync_session(self) -> Session:
        """
        Convierte la sesión async a sync para el agente
        """
        # Para simplificar, creamos una nueva sesión sync
        from app.database import engine
        return Session(engine)
        
    async def _get_group_participants(self, group_id: uuid.UUID) -> List[UserPreferences]:
        """
        Obtiene los participantes del grupo con sus preferencias
        """
        # Obtener miembros del grupo
        from sqlalchemy import select
        stmt = select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.status == True
        )
        result = await self.db.execute(stmt)
        group_members = result.scalars().all()
        
        participants = []
        for member in group_members:
            # Obtener información del usuario
            stmt = select(User).where(User.id == member.user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                # Por ahora usamos valores por defecto para las preferencias
                # En el futuro esto se puede conectar con un sistema de preferencias
                participant = UserPreferences(
                    user_id=user.id,
                    name=user.name,
                    destinations=["Cualquier destino"],  # Por defecto
                    activities=["Actividades generales"],
                    prices=["Medio"],
                    accommodations=["Hotel"],
                    transport=["Avión"],
                    motivations=["Explorar"]
                )
                participants.append(participant)
                
        return participants
        
    async def _get_chat_history(self, group_id: uuid.UUID, limit: int = 10) -> List[Dict]:
        """
        Obtiene el historial de chat del grupo
        """
        from sqlalchemy import select
        stmt = select(IAChat).where(
            IAChat.group_id == group_id,
            IAChat.status == True
        ).order_by(IAChat.created_at.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        # Convertir a formato esperado por el agente
        chat_history = []
        for msg in reversed(messages):  # Invertir para orden cronológico
            chat_history.append({
                "user_id": msg.user_id,
                "message": msg.message,
                "created_at": msg.created_at
            })
            
        return chat_history
        
    async def _get_or_create_trip(self, group_id: uuid.UUID) -> Trip:
        """
        Obtiene o crea un viaje para el grupo. Antes de crear uno nuevo, desactiva todos los viajes activos previos del grupo.
        """
        from sqlalchemy import select, update
        # Desactivar todos los viajes activos previos
        await self.db.execute(
            update(Trip)
            .where(Trip.group_id == group_id, Trip.status == True)
            .values(status=False)
        )
        await self.db.commit()
        # Buscar si hay un viaje activo (debería no haber tras el update)
        stmt = select(Trip).where(
            Trip.group_id == group_id,
            Trip.status == True
        )
        result = await self.db.execute(stmt)
        trip = result.scalar_one_or_none()
        if not trip:
            # Crear un nuevo viaje
            trip = Trip(
                id=uuid.uuid4(),
                group_id=group_id,
                destination="Por definir",
                start_date=None,
                end_date=None,
                status=True
            )
            self.db.add(trip)
            await self.db.commit()
            await self.db.refresh(trip)
        return trip
        
    async def process_message(
        self, 
        user_id: uuid.UUID, 
        group_id: uuid.UUID, 
        message: str
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje usando el agente de viajes personalizado
        """
        try:
            # Obtener o crear el viaje
            trip = await self._get_or_create_trip(group_id)
            
            # Obtener participantes del grupo
            participants = await self._get_group_participants(group_id)
            
            # Obtener historial de chat
            chat_history = await self._get_chat_history(group_id)
            
            # Crear contexto del viaje
            trip_context = TripContext(
                participants=participants,
                chat_history=chat_history,
                specific_requirements=message,
                group_id=group_id
            )
            
            # Crear sesión sync para el agente
            sync_db = await self._get_sync_session()
            
            try:
                # Crear instancia del agente
                agent = TripPlannerAgent(db=sync_db)
                
                # Procesar el mensaje con el agente
                response = await self._run_agent_async(agent, trip_context, trip.id)

                # Intentar guardar vuelos, hoteles e itinerario si hay JSON válido
                import re
                try:
                    json_match = re.search(r'```json\s*([\s\S]+?)```', response)
                    if json_match:
                        data = json.loads(json_match.group(1))
                        # Limpiar registros previos
                        await self.db.execute(Flight.__table__.delete().where(Flight.trip_id == trip.id))
                        await self.db.execute(Hotel.__table__.delete().where(Hotel.trip_id == trip.id))
                        await self.db.execute(Itinerary.__table__.delete().where(Itinerary.trip_id == trip.id))
                        # Guardar vuelos
                        for vuelo in data.get("vuelos", []):
                            flight = Flight(
                                trip_id=trip.id,
                                airline=vuelo.get("aerolínea", "No especificada"),
                                departure_airport=vuelo.get("origen", ""),
                                arrival_airport=vuelo.get("destino", ""),
                                departure_time=None,
                                arrival_time=None,
                                price=float(vuelo.get("precio", "0").replace("$", "").replace(",", "") or 0),
                                status=True
                            )
                            self.db.add(flight)
                        # Guardar hoteles
                        for hotel in data.get("hoteles", []):
                            hotel_obj = Hotel(
                                trip_id=trip.id,
                                name=hotel.get("nombre", hotel.get("ciudad", "")),
                                location=hotel.get("ciudad", ""),
                                price_per_night=float(hotel.get("precio", "0").replace("$", "").replace("€", "").replace(",", "") or 0),
                                rating=None,
                                link=None,
                                status=True
                            )
                            self.db.add(hotel_obj)
                        # Guardar itinerario
                        from datetime import date, timedelta, time
                        if "itinerary_days" in data:
                            start_date = trip.start_date or date.today()
                            for day in data["itinerary_days"]:
                                day_num = day.get("day", 1)
                                activities = day.get("activities", [])
                                for act in activities:
                                    # Parsear hora
                                    time_str = act.get("time", "09:00")
                                    try:
                                        start_time = time.fromisoformat(time_str)
                                        end_time = (time.fromisoformat(time_str).replace(hour=(int(time_str[:2]) + 2) % 24))
                                    except:
                                        start_time = None
                                        end_time = None
                                    itinerary = Itinerary(
                                        trip_id=trip.id,
                                        day=start_date + timedelta(days=day_num - 1),
                                        activity=act.get("activity", ""),
                                        location=act.get("location", ""),
                                        start_time=start_time,
                                        end_time=end_time,
                                        status=True
                                    )
                                    self.db.add(itinerary)
                        await self.db.commit()
                except Exception as e:
                    print("[WARN] No se pudo guardar vuelos/hoteles/itinerario:", e)

                return {
                    "success": True,
                    "response": response,
                    "trip_id": str(trip.id)
                }
                
            finally:
                sync_db.close()
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Lo siento, hubo un error procesando tu mensaje: {str(e)}"
            }
            
    async def _run_agent_async(self, agent: TripPlannerAgent, context: TripContext, trip_id: uuid.UUID) -> str:
        """
        Ejecuta el agente de forma asíncrona
        """
        # El agente ya es async, solo necesitamos llamarlo directamente
        return await agent.process_message(context, trip_id)
        
    async def save_agent_response(
        self, 
        user_id: uuid.UUID, 
        group_id: uuid.UUID, 
        response: str
    ) -> IAChat:
        """
        Guarda la respuesta del agente en la base de datos
        """
        agent_message = IAChat(
            user_id=user_id,
            group_id=group_id,
            message=response
        )
        
        self.db.add(agent_message)
        await self.db.commit()
        await self.db.refresh(agent_message)
        
        return agent_message 