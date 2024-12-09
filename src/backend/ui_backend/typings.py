
from pydantic import BaseModel
from flowagent.data import Conversation

class SingleRegisterResponse(BaseModel):
    conversation_id: str
    success: bool
    conversation: Conversation

class SingleBotPredictRequest(BaseModel):
    query: str