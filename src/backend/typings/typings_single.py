
from typing import Dict, Optional
from pydantic import BaseModel
from flowagent.data import Conversation, APIOutput, BotOutput, Config

class SingleRegisterRequest(BaseModel):
    user_identity: Optional[Dict] = None
    config: Config

class SingleRegisterResponse(BaseModel):
    conversation_id: str
    success: bool
    conversation: Conversation

class SinglePostControlResponse(BaseModel):
    success: bool
    msg: str


class SingleToolResponse(BaseModel):
    api_output: APIOutput
    msg: str

class SingleBotPredictResponse(BaseModel):
    bot_output: BotOutput
    msg: str
