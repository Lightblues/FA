"""
ref:
    https://github.com/geekan/MetaGPT/blob/main/metagpt/context_mixin.py
"""

from pydantic import BaseModel, Field

from common import Config
from data import BotOutput, Conversation, DataHandler


class Context(BaseModel):
    cfg: Config = Field(default=Config())
    data_handler: DataHandler = Field(default=DataHandler())
    conv: Conversation = Field(default=Conversation())


# class ContextMixin(BaseModel):
#     context: Context = Field(default=None, exclude=True)
#     def set_context(self, context: Context):
#         self.context = context
