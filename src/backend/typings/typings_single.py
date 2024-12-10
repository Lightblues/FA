
from pydantic import BaseModel
from flowagent.data import Conversation, APIOutput, BotOutput, Config

class SingleRegisterResponse(BaseModel):
    conversation_id: str
    success: bool
    conversation: Conversation

class SingleBotPredictRequest(BaseModel):
    query: str

class SinglePostControlResponse(BaseModel):
    success: bool
    content: str

SingleRegisterRequest = Config
SingleToolResponse = APIOutput
SingleBotPredictResponse = BotOutput