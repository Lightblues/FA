from typing import Dict
from .base import BaseRole, BaseAPIHandler, BaseBot, BaseUser
from .api import DummyAPIHandler
from .user import DummyUser, InputUser
from .bot import DummyBot


USER_NAME2CLASS:Dict[str, BaseUser] = {}
for cls in BaseUser.__subclasses__():
    for name in cls.names:
        USER_NAME2CLASS[name] = cls
BOT_NAME2CLASS: Dict[str, BaseBot] = {}
for cls in BaseBot.__subclasses__():
    for name in cls.names:
        BOT_NAME2CLASS[name] = cls
API_NAME2CLASS:Dict[str, BaseAPIHandler] = {}
for cls in BaseAPIHandler.__subclasses__():
    for name in cls.names:
        API_NAME2CLASS[name] = cls