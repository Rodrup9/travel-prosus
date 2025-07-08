from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from pydantic import BaseModel

class FlightPrice(BaseModel):
    airline: str
    airline_name: Optional[str] = None
    departure_time: str
    arrival_time: str
    departure_airport: str
    arrival_airport: str
    price: float
    currency: str = "USD"
    class_type: str
    stops: int
    duration: Optional[str] = None
    available_seats: Optional[int] = None

class HotelPrice(BaseModel):
    hotel_name: str
    location: str
    price_per_night: float
    currency: str = "USD"
    room_type: str
    amenities: List[str]
    rating: Optional[float] = None
    description: Optional[str] = None
    address: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    available_rooms: Optional[int] = None

class Airport(BaseModel):
    iata_code: str
    name: str
    city: str
    country: str
    latitude: float
    longitude: float

class City(BaseModel):
    iata_code: str
    name: str
    country: str
    timezone: str

class TravelPriceSearcher:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        # Usar URL de sandbox por defecto (tu key es de sandbox)
        self.base_url = "https://test.api.amadeus.com"  # URL de sandbox
        self.access_token = None
        self._token_expiry = None
        
    def _get_access_token(self) -> str:
        """
        Obtiene el token de acceso de Amadeus
        """
        # Si el token existe y no ha expirado, lo retornamos
        if self.access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self.access_token
            
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
        data = response.json()
        self.access_token = data["access_token"]
        # Guardamos la expiración del token (típicamente 30 minutos)
        self._token_expiry = datetime.now() + timedelta(seconds=data.get("expires_in", 1800))
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
            
        endpoint = f"{self.base_url}/v1/shopping/flight-offers"
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
            "currencyCode": "USD",
            "nonStop": "false",  # Incluir vuelos con escalas
            "includedAirlineCodes": None  # Todas las aerolíneas
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
                # Calcular duración total
                departure = datetime.fromisoformat(itinerary["segments"][0]["departure"]["at"].replace("Z", "+00:00"))
                arrival = datetime.fromisoformat(itinerary["segments"][-1]["arrival"]["at"].replace("Z", "+00:00"))
                duration = str(arrival - departure)
                
                flight = FlightPrice(
                    airline=itinerary["segments"][0]["carrierCode"],
                    airline_name=itinerary["segments"][0].get("operating", {}).get("carrierCode"),
                    departure_time=itinerary["segments"][0]["departure"]["at"],
                    arrival_time=itinerary["segments"][-1]["arrival"]["at"],
                    departure_airport=itinerary["segments"][0]["departure"]["iataCode"],
                    arrival_airport=itinerary["segments"][-1]["arrival"]["iataCode"],
                    price=float(offer["price"]["total"]),
                    currency=offer["price"]["currency"],
                    class_type=offer["travelerPricings"][0]["fareDetailsBySegment"][0]["cabin"],
                    stops=len(itinerary["segments"]) - 1,
                    duration=duration,
                    available_seats=offer["numberOfBookableSeats"]
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
            
        endpoint = f"{self.base_url}/v2/shopping/hotel-offers"
        
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
            "sort": "PRICE",
            "currency": "USD"
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
                rating=hotel.get("rating"),
                description=hotel.get("description", {}).get("text"),
                address=f"{hotel['address'].get('lines', [''])[0]}, {hotel['address']['cityName']}, {hotel['address']['countryCode']}",
                check_in=hotel.get("checkInTime"),
                check_out=hotel.get("checkOutTime"),
                available_rooms=price_info.get("roomQuantity")
            )
            hotels.append(hotel_price)
            
        return hotels[:max_results]

    def search_city(self, keyword: str) -> List[City]:
        """
        Busca ciudades usando la API de Amadeus
        
        Args:
            keyword: Texto para buscar la ciudad
        """
        if not self.access_token:
            self._get_access_token()
            
        endpoint = f"{self.base_url}/reference-data/locations"
        params = {
            "subType": "CITY",
            "keyword": keyword,
            "page[limit]": 10
        }
        
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.access_token}"},
            params=params
        )
        response.raise_for_status()
        
        cities = []
        for data in response.json().get("data", []):
            city = City(
                iata_code=data["iataCode"],
                name=data["name"],
                country=data["address"]["countryName"],
                timezone=data.get("timeZone", {}).get("name", "UTC")
            )
            cities.append(city)
            
        return cities

    def search_airport(self, keyword: str) -> List[Airport]:
        """
        Busca aeropuertos usando la API de Amadeus
        
        Args:
            keyword: Texto para buscar el aeropuerto
        """
        if not self.access_token:
            self._get_access_token()
            
        endpoint = f"{self.base_url}/reference-data/locations"
        params = {
            "subType": "AIRPORT",
            "keyword": keyword,
            "page[limit]": 10
        }
        
        response = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.access_token}"},
            params=params
        )
        response.raise_for_status()
        
        airports = []
        for data in response.json().get("data", []):
            airport = Airport(
                iata_code=data["iataCode"],
                name=data["name"],
                city=data["address"]["cityName"],
                country=data["address"]["countryName"],
                latitude=float(data["geoCode"]["latitude"]),
                longitude=float(data["geoCode"]["longitude"])
            )
            airports.append(airport)
            
        return airports

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
                    "airline": f"{f.airline} ({f.airline_name})" if f.airline_name else f.airline,
                    "departure": {
                        "time": f.departure_time,
                        "airport": f.departure_airport
                    },
                    "arrival": {
                        "time": f.arrival_time,
                        "airport": f.arrival_airport
                    },
                    "price": f"{f.price:.2f} {f.currency}",
                    "class": f.class_type,
                    "stops": f.stops,
                    "duration": f.duration,
                    "available_seats": f.available_seats
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
                    "rating": h.rating,
                    "description": h.description[:200] + "..." if h.description and len(h.description) > 200 else h.description,
                    "address": h.address,
                    "check_in": h.check_in,
                    "check_out": h.check_out,
                    "available_rooms": h.available_rooms
                }
                for h in hotels
            ]
            
        return results 