import datetime, os, re, yaml, copy, pathlib
from enum import Enum, auto
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple


@dataclass
class Config:
    conversation_turn_limit: int = 20
    bot_action_limit: int = 5


@dataclass
class Workflow:
    pass


class BotOutputType(Enum):
    RESPONSE = ("RESPONSE", "response to the user")
    ACTION = ("ACTION", "call an API")

    def __init__(self, actionname, description):
        self.actionname = actionname
        self.description = description


@dataclass
class UserOutput:
    pass

@dataclass
class BotOutput:
    thought: str = None
    action: str = None
    action_input: str = None
    response: str = None
    
    @property
    def action_type(self) -> BotOutputType:
        if self.action is not None:
            return BotOutputType.ACTION
        else:
            return BotOutputType.RESPONSE

@dataclass
class APIOutput:
    pass