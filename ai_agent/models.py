from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

class UserPreferences(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    user_id: uuid.UUID
    name: str
    destinations: List[str]
    activities: List[str]
    prices: List[str]
    accommodations: List[str]
    transport: List[str]
    motivations: List[str]

class GroupChatMessage(BaseModel):
    user_id: str
    group_id: str
    message: str
    status: bool
    id: str
    created_at: datetime

class ChatMessage(BaseModel):
    user_id: uuid.UUID
    message: str
    created_at: datetime

class TripContext(BaseModel):
    participants: List[UserPreferences]
    chat_history: List[ChatMessage]
    specific_requirements: Optional[str] = None
    group_id: uuid.UUID

class AgentResponse(BaseModel):
    itinerary: str
    reasoning: Optional[str] = None
    additional_suggestions: Optional[List[str]] = None
    error: Optional[str] = None 