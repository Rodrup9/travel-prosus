from typing import Dict, List, Optional
from datetime import datetime
import requests
from pydantic import BaseModel

class FlightPrice(BaseModel):
    airline: str
    departure_time: str
    arrival_time: str
    price: float
    currency: str = "USD"
    class_type: str
    stops: int

class HotelPrice(BaseModel):
    hotel_name: str
    location: str
    price_per_night: float
    currency: str = "USD"
    room_type: str
    amenities: List[str]
    rating: Optional[float] = None

class TravelPriceSearcher:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://test.api.amadeus.com/v1"  # URL base de Amadeus
        self.access_token = None
        
    def _get_access_token(self) -> str:
        """
        Obtiene el token de acceso de Amadeus
        """
        auth_url = f"{self.base_url}/security/oauth2/token"
        response = requests.post(
            auth_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            }
        )
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        return self.access_token

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        max_results: int = 5
    ) -> List[FlightPrice]:
        """
        Busca vuelos usando la API de Amadeus
        
        Args:
            origin: Código IATA del aeropuerto de origen
            destination: Código IATA del aeropuerto de destino
            departure_date: Fecha de salida (YYYY-MM-DD)
            return_date: Fecha de retorno (YYYY-MM-DD), opcional
            adults: Número de adultos
            max_results: Número máximo de resultados a retornar
        """
        if not self.access_token:
            self._get_access_token()
            
        endpoint = f"{self.base_url}/shopping/flight-offers"
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
            "currencyCode": "USD"
        }
        
        if return_date:
            params["returnDate"] = return_date
            
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.access_token}"},
            params=params
        )
        response.raise_for_status()
        
        flights = []
        for offer in response.json()["data"]:
            for itinerary in offer["itineraries"]:
                flight = FlightPrice(
                    airline=itinerary["segments"][0]["carrierCode"],
                    departure_time=itinerary["segments"][0]["departure"]["at"],
                    arrival_time=itinerary["segments"][-1]["arrival"]["at"],
                    price=float(offer["price"]["total"]),
                    currency=offer["price"]["currency"],
                    class_type=offer["travelerPricings"][0]["fareDetailsBySegment"][0]["cabin"],
                    stops=len(itinerary["segments"]) - 1
                )
                flights.append(flight)
                
        return flights

    def search_hotels(
        self,
        city: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        max_results: int = 5
    ) -> List[HotelPrice]:
        """
        Busca hoteles usando la API de Amadeus
        
        Args:
            city: Código de ciudad
            check_in: Fecha de check-in (YYYY-MM-DD)
            check_out: Fecha de check-out (YYYY-MM-DD)
            guests: Número de huéspedes
            max_results: Número máximo de resultados a retornar
        """
        if not self.access_token:
            self._get_access_token()
            
        endpoint = f"{self.base_url}/shopping/hotel-offers"
        
        params = {
            "cityCode": city,
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "adults": guests,
            "radius": 50,
            "radiusUnit": "KM",
            "paymentPolicy": "ANY",
            "includeClosed": False,
            "bestRateOnly": True,
            "view": "FULL",
            "sort": "PRICE"
        }
        
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.access_token}"},
            params=params
        )
        response.raise_for_status()
        
        hotels = []
        for offer in response.json()["data"]:
            hotel = offer["hotel"]
            price_info = offer["offers"][0]
            
            hotel_price = HotelPrice(
                hotel_name=hotel["name"],
                location=f"{hotel['address']['cityName']}, {hotel['address']['countryCode']}",
                price_per_night=float(price_info["price"]["total"]) / (
                    datetime.strptime(check_out, "%Y-%m-%d") - 
                    datetime.strptime(check_in, "%Y-%m-%d")
                ).days,
                currency=price_info["price"]["currency"],
                room_type=price_info["room"]["type"],
                amenities=hotel.get("amenities", []),
                rating=hotel.get("rating")
            )
            hotels.append(hotel_price)
            
        return hotels[:max_results]

    def format_results_for_agent(
        self,
        flights: Optional[List[FlightPrice]] = None,
        hotels: Optional[List[HotelPrice]] = None
    ) -> Dict:
        """
        Formatea los resultados para el agente de IA
        """
        results = {
            "flights": [],
            "hotels": []
        }
        
        if flights:
            results["flights"] = [
                {
                    "airline": f.airline,
                    "departure": f.departure_time,
                    "arrival": f.arrival_time,
                    "price": f"{f.price:.2f} {f.currency}",
                    "class": f.class_type,
                    "stops": f.stops
                }
                for f in flights
            ]
            
        if hotels:
            results["hotels"] = [
                {
                    "name": h.hotel_name,
                    "location": h.location,
                    "price": f"{h.price_per_night:.2f} {h.currency}/night",
                    "room": h.room_type,
                    "amenities": h.amenities[:5],  # Limitamos a 5 amenities para no sobrecargar
                    "rating": h.rating
                }
                for h in hotels
            ]
            
        return results 