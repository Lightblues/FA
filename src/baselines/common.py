import datetime, os, re, yaml, copy, pathlib, time
from enum import Enum, auto
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Tuple, Union


@dataclass
class Config:
    conversation_turn_limit: int = 20
    
    user_mode: str = "base_user"
    
    bot_mode: str = "base_bot"
    bot_action_limit: int = 5
    
    api_mode: str = "base_api"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_yaml(cls, yaml_file: str, normalize: bool = True):
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        obj = cls(**data)
        return obj


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
    is_success: bool = None
    


class Timer:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        print(f"  <timer> {self.name} took {self.elapsed_time:.4f} seconds")
