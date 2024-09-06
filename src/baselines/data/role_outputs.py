import datetime, os, re, yaml, copy, pathlib, time
from enum import Enum, auto
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple, Union


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
    
    thought_str = "Thought"
    action_str = "Action"
    action_input_str = "Action Input"
    response_str = "Response"
    
    @property
    def action_type(self) -> BotOutputType:
        if self.action is not None:
            return BotOutputType.ACTION
        else:
            assert self.response is not None, "both action and response are None!"
            return BotOutputType.RESPONSE

@dataclass
class APIOutput:
    is_success: bool = None