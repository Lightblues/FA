
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

class SingleToolResponse(BaseModel):
    api_output: APIOutput
    msg: str

class SingleBotPredictResponse(BaseModel):
    bot_output: BotOutput
    msg: str
