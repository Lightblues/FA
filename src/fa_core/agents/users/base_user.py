from typing import Any, ClassVar, List

from pydantic import BaseModel, Field

from fa_core.data import UserOutput


class BaseUser(BaseModel):
    names: ClassVar[List[str]] = ["base_user"]
    user_template_fn: str = ""  # for get LLM prompt
    cnt_user_queries: int = Field(default=0)

    def model_post_init(self, __context: Any) -> None:
        # overwrite the default template
        if self.cfg.user_template_fn is not None:
            self.user_template_fn = self.cfg.user_template_fn

    def process(self, *args, **kwargs) -> UserOutput:
        """
        1. generate user query (free style?)
        """
        raise NotImplementedError
