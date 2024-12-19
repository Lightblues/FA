from typing import Dict, Optional

from pydantic import BaseModel

from common import Config
from flowagent.data import APIOutput, BotOutput, Conversation

from .typings_base import BaseResponse


class SingleRegisterRequest(BaseModel):
    user_identity: Optional[Dict] = None
    config: Config


class SingleRegisterResponse(BaseResponse):
    conversation_id: str
    success: bool
    conversation: Conversation
    pdl_str: str


class SinglePostControlResponse(BaseResponse):
    success: bool
    msg: str


class SingleToolResponse(BaseResponse):
    api_output: APIOutput
    msg: str


class SingleBotPredictResponse(BaseResponse):
    bot_output: BotOutput
    msg: str
