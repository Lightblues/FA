import collections
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from common import Config
from data import APIOutput
from fa.envs import Context


class BaseTool(BaseModel):
    names: ClassVar[List[str]] = ["base_tool"]

    cfg: Config = Field(default=None)  # bot_llm_name, bot_template_fn
    context: Context = Field(default=None)  # , exclude=True)  # NOTE: avoid circular import
    api_infos: List[Dict] = Field(default_factory=list)  # TODO: add typing for api_infos

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._post_init()

    def _post_init(self) -> None:
        """e.g. see [[request_tool.py]]"""
        pass

    def process(self, *args, **kwargs) -> APIOutput:
        """
        1. match and check the validity of API
        2. call the API (with retry?)
        3. parse the response
        """
        raise NotImplementedError
