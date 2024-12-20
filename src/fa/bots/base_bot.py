from typing import Any, ClassVar, Iterator, List, Tuple

from pydantic import BaseModel, Field

from common import Config, OpenAIClient, init_client
from data import BotOutput
from fa.envs import Context


class BaseBot(BaseModel):
    names: ClassVar[List[str]] = ["base_bot"]

    cfg: Config = Field(default=None)  # bot_llm_name, bot_template_fn
    context: Context = Field(default=None)  # , exclude=True)  # NOTE: avoid circular import

    bot_template_fn: str = ""
    bot_llm_name: str = ""
    llm: OpenAIClient = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._post_init()

    def _post_init(self) -> None:
        """e.g. init the llm"""
        pass

    """
    NOTE: two APIs
    1. .process();
    2. .process_stream() then .process_LLM_response()
    """

    def process(self, *args, **kwargs) -> BotOutput:
        """
        1. generate ReAct format output by LLM
        2. parse to BotOutput
        """
        raise NotImplementedError

    def process_stream(self) -> Tuple[str, Iterator[str]]:
        raise NotImplementedError

    def process_LLM_response(self) -> BotOutput:
        raise NotImplementedError
