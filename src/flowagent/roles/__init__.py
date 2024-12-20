from enum import Enum
from typing import Dict

from .base import BaseBot, BaseRole, BaseTool, BaseUser
from .bots import (
    CoREBot,
    DummyBot,
    PDLBot,
)
from .tools import CoREAPIHandler, DummyTool, LLMSimulatedTool
from .user import DummyUser


def build_attr_map(base_class: BaseRole, name_to_class_dict: Dict[str, BaseRole], attr: str = "names"):
    for cls in base_class.__subclasses__():
        if attr in cls.__dict__:
            name_to_class_dict[cls.__dict__[attr]] = cls
        build_attr_map(cls, name_to_class_dict, attr)


USER_NAME2TEMPLATE: Dict[str, str] = {}
build_attr_map(BaseUser, USER_NAME2TEMPLATE, attr="user_template_fn")
BOT_NAME2TEMPLATE: Dict[str, str] = {}
build_attr_map(BaseBot, BOT_NAME2TEMPLATE, attr="bot_template_fn")
API_NAME2TEMPLATE: Dict[str, str] = {}
build_attr_map(BaseTool, API_NAME2TEMPLATE, attr="api_template_fn")


# for typer
def create_enum(name, values):
    return Enum(name, {key: key for key in values})


# UserMode = create_enum("UserMode", USER_NAME2CLASS.keys())
# BotMode = create_enum("BotMode", BOT_NAME2CLASS.keys())
# ApiMode = create_enum("ApiMode", API_NAME2CLASS.keys())
