from typing import List
from app.models.preferences import UserPreferenceResponse, UserPreferenceBase
from ai_agent.models import UserProfile

class AgentPreferencesService:
    @staticmethod
    def transform_preferences_to_agent_format(preferences: UserPreferenceResponse) -> List[UserProfile]:
        """
        Transforma las preferencias de Neo4j al formato que necesita el agente
        """
        agent_profiles = []
        
        for user_pref in preferences.data:
            # Combinar todas las preferencias como intereses
            interests = (
                user_pref.Destinos +
                user_pref.Actividades +
                user_pref.Motivaciones
            )
            
            # Crear diccionario de preferencias de viaje
            travel_preferences = {
                "accommodation": user_pref.Alojamientos,
                "transport": user_pref.Transportes
            }
            
            # Obtener la preferencia de precio (tomamos la primera si hay varias)
            budget_preference = user_pref.Precios[0] if user_pref.Precios else None
            
            # Crear perfil de usuario para el agente
            profile = UserProfile(
                user_id=user_pref.sql_id,
                interests=interests,
                travel_preferences=travel_preferences,
                budget_preference=budget_preference
            )
            
            agent_profiles.append(profile)
            
        return agent_profiles 