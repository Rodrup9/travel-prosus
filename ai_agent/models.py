from typing import List, Optional
from pydantic import BaseModel

class UserProfile(BaseModel):
    user_id: str
    interests: List[str]
    travel_preferences: Optional[dict] = None
    budget_preference: Optional[str] = None

class ChatMessage(BaseModel):
    message_id: str
    user_id: str
    content: str
    timestamp: str

class TripContext(BaseModel):
    trip_id: str
    participants: List[UserProfile]
    chat_history: List[ChatMessage]
    specific_requirements: Optional[str] = None

class AgentResponse(BaseModel):
    itinerary: str
    reasoning: Optional[str] = None
    additional_suggestions: Optional[List[str]] = None
    error: Optional[str] = None 