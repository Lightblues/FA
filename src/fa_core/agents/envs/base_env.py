"""
ref:
    https://github.com/geekan/MetaGPT/blob/main/metagpt/context_mixin.py
"""

from typing import Dict

from pydantic import BaseModel, Field

from fa_core.common import Config
from fa_core.data import BotOutput, Conversation, FAWorkflow


class Context(BaseModel):
    cfg: Config
    workflow: FAWorkflow
    conv: Conversation

    status_for_prompt: Dict[str, str] = Field(default_factory=dict)  # for PDLBot's prompt


# class ContextMixin(BaseModel):
#     context: Context = Field(default=None, exclude=True)
#     def set_context(self, context: Context):
#         self.context = context