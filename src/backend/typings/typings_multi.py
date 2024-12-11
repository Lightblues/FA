
from typing import Dict, Optional, Any
from pydantic import BaseModel
from flowagent.data import (
    Message, Conversation, APIOutput, Config,
    MainBotOutput, WorkflowBotOutput
)

class MultiRegisterRequest(BaseModel):
    user_identity: Optional[Dict] = None
    config: Config

class MultiRegisterResponse(BaseModel):
    conversation_id: str
    success: bool
    conversation: Conversation

class MultiPostControlResponse(BaseModel):
    success: bool
    msg: Optional[Message] = None


class MultiToolWorkflowResponse(BaseModel):
    api_output: APIOutput
    msg: Message

class MultiBotWorkflowPredictResponse(BaseModel):
    bot_output: WorkflowBotOutput
    msg: Message

class MultiToolMainResponse(BaseModel):
    tool_output: Any
    msg: Message

class MultiBotMainPredictResponse(BaseModel):
    bot_output: MainBotOutput
    msg: Message
