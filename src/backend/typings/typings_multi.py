from typing import Dict, Optional

from pydantic import BaseModel

from flowagent.data import (
    APIOutput,
    Config,
    Conversation,
    MainBotOutput,
    Message,
    WorkflowBotOutput,
)

from .typings_base import BaseResponse


class MultiRegisterRequest(BaseModel):
    user_identity: Optional[Dict] = None
    config: Config


class MultiRegisterResponse(BaseResponse):
    conversation_id: str
    success: bool
    conversation: Conversation


class MultiPostControlResponse(BaseResponse):
    success: bool
    msg: Optional[Message] = None


class MultiToolWorkflowResponse(BaseResponse):
    api_output: APIOutput
    msg: Message


class MultiBotWorkflowPredictResponse(BaseResponse):
    bot_output: WorkflowBotOutput
    msg: Message


class MultiToolMainResponse(BaseResponse):
    tool_output: Optional[str] = None
    msg: Message


class MultiBotMainPredictResponse(BaseResponse):
    bot_output: MainBotOutput
    msg: Message
