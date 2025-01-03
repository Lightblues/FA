from typing import Dict, Optional

from pydantic import BaseModel

from fa_core.common import Config
from fa_core.data import APIOutput, BotOutput, Conversation

from .typings_base import BaseResponse


class SingleRegisterRequest(BaseModel):
    user_identity: Optional[Dict] = None
    config: Config


class SingleRegisterResponse(BaseResponse):
    conversation_id: str
    success: bool
    conversation: Conversation
    pdl_str: str  # without Procedure
    procedure_str: str


class SinglePostControlResponse(BaseResponse):
    success: bool
    msg: str


class SingleToolResponse(BaseResponse):
    api_output: APIOutput
    msg: str


class SingleBotPredictResponse(BaseResponse):
    bot_output: BotOutput
    msg: str
