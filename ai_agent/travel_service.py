from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.flight import Flight
from app.models.hotel import Hotel
from app.models.trip import Trip
from .travel_tools import FlightPrice, HotelPrice, TravelPriceSearcher
import uuid

class TravelService:
    def __init__(self, db: AsyncSession, api_key: str, api_secret: str):
        self.db = db
        self.searcher = TravelPriceSearcher(api_key=api_key, api_secret=api_secret)
        
    async def search_and_save_flights(
        self,
        trip_id: uuid.UUID,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        max_results: int = 5
    ) -> List[Flight]:
        """
        Busca vuelos y guarda los resultados en la base de datos
        """
        # Buscar vuelos usando Amadeus
        flights = self.searcher.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            max_results=max_results
        )
        
        # Guardar resultados en la base de datos
        db_flights = []
        for flight in flights:
            db_flight = Flight(
                id=uuid.uuid4(),
                trip_id=trip_id,
                airline=flight.airline,
                departure_airport=flight.departure_airport,
                arrival_airport=flight.arrival_airport,
                departure_time=datetime.fromisoformat(flight.departure_time.replace("Z", "+00:00")),
                arrival_time=datetime.fromisoformat(flight.arrival_time.replace("Z", "+00:00")),
                price=flight.price,
                status=True
            )
            self.db.add(db_flight)
            db_flights.append(db_flight)
            
        await self.db.commit()
        for flight in db_flights:
            await self.db.refresh(flight)
            
        return db_flights
        
    async def search_and_save_hotels(
        self,
        trip_id: uuid.UUID,
        city: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        max_results: int = 5
    ) -> List[Hotel]:
        """
        Busca hoteles y guarda los resultados en la base de datos
        """
        # Buscar hoteles usando Amadeus
        hotels = self.searcher.search_hotels(
            city=city,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            max_results=max_results
        )
        
        # Guardar resultados en la base de datos
        db_hotels = []
        for hotel in hotels:
            db_hotel = Hotel(
                id=uuid.uuid4(),
                trip_id=trip_id,
                name=hotel.hotel_name,
                location=hotel.location,
                price_per_night=hotel.price_per_night,
                rating=hotel.rating or 0.0,
                link=hotel.address or "",  # Usamos la dirección como link por ahora
                status=True
            )
            self.db.add(db_hotel)
            db_hotels.append(db_hotel)
            
        await self.db.commit()
        for hotel in db_hotels:
            await self.db.refresh(hotel)
            
        return db_hotels
        
    async def get_trip_flights(self, trip_id: uuid.UUID) -> List[Flight]:
        """
        Obtiene los vuelos guardados para un viaje
        """
        stmt = select(Flight).where(
            Flight.trip_id == trip_id,
            Flight.status == True
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
        
    async def get_trip_hotels(self, trip_id: uuid.UUID) -> List[Hotel]:
        """
        Obtiene los hoteles guardados para un viaje
        """
        stmt = select(Hotel).where(
            Hotel.trip_id == trip_id,
            Hotel.status == True
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
        
    async def clear_trip_results(self, trip_id: uuid.UUID) -> None:
        """
        Marca como inactivos todos los resultados anteriores de un viaje
        """
        from sqlalchemy import update
        stmt = update(Flight).where(Flight.trip_id == trip_id).values(status=False)
        await self.db.execute(stmt)
        stmt = update(Hotel).where(Hotel.trip_id == trip_id).values(status=False)
        await self.db.execute(stmt)
        await self.db.commit()
        
    async def format_saved_results(
        self,
        flights: Optional[List[Flight]] = None,
        hotels: Optional[List[Hotel]] = None
    ) -> dict:
        """
        Formatea los resultados guardados en la base de datos para el agente
        """
        results = {
            "flights": [],
            "hotels": []
        }
        
        if flights:
            results["flights"] = [
                {
                    "airline": f.airline,
                    "departure": {
                        "time": f.departure_time.isoformat(),
                        "airport": f.departure_airport
                    },
                    "arrival": {
                        "time": f.arrival_time.isoformat(),
                        "airport": f.arrival_airport
                    },
                    "price": f"{f.price:.2f} USD",
                }
                for f in flights
            ]
            
        if hotels:
            results["hotels"] = [
                {
                    "name": h.name,
                    "location": h.location,
                    "price": f"{h.price_per_night:.2f} USD/night",
                    "rating": h.rating,
                    "address": h.link  # El link contiene la dirección
                }
                for h in hotels
            ]
            
        return results 