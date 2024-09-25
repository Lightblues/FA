from typing import Dict
from enum import Enum
from .base import BaseRole, BaseAPIHandler, BaseBot, BaseUser
from .api import DummyAPIHandler
from .user import DummyUser, InputUser
from .bot import DummyBot, PDLBot

def add_subclasses_to_dict(base_class: BaseRole, name_to_class_dict: Dict[str, BaseRole]):
    for cls in base_class.__subclasses__():
        for name in cls.names:
            name_to_class_dict[name] = cls
        # recursive!
        add_subclasses_to_dict(cls, name_to_class_dict)

USER_NAME2CLASS:Dict[str, BaseUser] = {}
add_subclasses_to_dict(BaseUser, USER_NAME2CLASS)
BOT_NAME2CLASS: Dict[str, BaseBot] = {}
add_subclasses_to_dict(BaseBot, BOT_NAME2CLASS)
API_NAME2CLASS:Dict[str, BaseAPIHandler] = {}
add_subclasses_to_dict(BaseAPIHandler, API_NAME2CLASS)

# for typer
def create_enum(name, values):
    return Enum(name, {key: key for key in values})
UserMode = create_enum('UserMode', USER_NAME2CLASS.keys())
BotMode = create_enum('BotMode', BOT_NAME2CLASS.keys())
ApiMode = create_enum('ApiMode', API_NAME2CLASS.keys())
