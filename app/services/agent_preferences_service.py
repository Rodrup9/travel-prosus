from typing import List
from app.models.preferences import UserPreferenceResponse, UserPreferenceBase
from ai_agent.models import UserPreferences
import uuid

class AgentPreferencesService:
    @staticmethod
    def transform_preferences_to_agent_format(preferences: UserPreferenceResponse) -> List[UserPreferences]:
        """
        Transforma las preferencias de Neo4j al formato que necesita el agente
        """
        agent_profiles = []
        
        for user_pref in preferences.data:
            # Convertir el sql_id a UUID
            user_id = uuid.UUID(user_pref.sql_id)
            
            # Mantener las preferencias separadas
            profile = UserPreferences(
                user_id=user_id,
                name=user_pref.Usuario,
                destinations=user_pref.Destinos,
                activities=user_pref.Actividades,
                prices=user_pref.Precios,
                accommodations=user_pref.Alojamientos,
                transport=user_pref.Transportes,
                motivations=user_pref.Motivaciones
            )
            
            agent_profiles.append(profile)
            
        return agent_profiles 