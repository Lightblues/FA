from typing import Any
from pydantic import BaseModel

from fa_demo.backend import FrontendClient, SingleBotPredictResponse
from fa_core.common import Config, LogUtils, get_session_id, init_loguru_logger
from fa_core.data import BotOutput, Conversation


class FixedQuerySimulator(BaseModel):
    cfg: Config
    client: FrontendClient
    conversation_id: str
    verbose: bool = False

    def model_post_init(self, __context: Any) -> None:
        self.conversation_id = get_session_id()
        self.client = FrontendClient(self.cfg.backend_url)
        self.conversation = self.client.single_register(self.conversation_id, self.cfg)
        return super().model_post_init(__context)

    def run(self) -> Conversation:
        return self.conversation
