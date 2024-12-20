from pydantic import BaseModel, Field

from common import Config
from data import Conversation, DataHandler


class Bot(BaseModel):
    context: "SessionContext" = Field(default=None, exclude=True)

    def set_context(self, context: "SessionContext"):
        self.context = context


class SessionContext(BaseModel):
    session_id: str = Field(default="123")
    cfg: Config = Field(default=Config())
    conv: Conversation = Field(default=Conversation())
    workflow: DataHandler = Field(default=DataHandler())
    bot: Bot = Field(default=None)

    def add_bot(self, bot: Bot):
        self.bot = bot
        bot.set_context(self)


context = SessionContext()
context.add_bot(Bot())

print(context.model_dump_json())
print(context.model_dump())
print(context.model_json_schema())

print(context.bot.model_dump_json())
print(context.bot.model_dump())
print(context.bot.model_json_schema())
