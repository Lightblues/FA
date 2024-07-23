""" 
@240712
"""
import datetime, os, re, yaml, copy
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from colorama import init, Fore, Style

from .pdl import PDL
from .common import DIR_huabu_step3, DataManager

# from engine_v1.datamodel import Role, Message, ActionType, Conversation

class ActionType(Enum):
    START = auto()
    API = auto()
    REQUEST = auto()
    ANSWER = auto()
    USER = auto()
    API_RESPONSE = auto()

    def __str__(self):
        return f"ActionType.{self.name}"

class Role(Enum):
    SYSTEM = (0, "[SYSTEM] ", "system", 'green')
    USER = (1, "[USER] ", "user", "red")
    BOT = (2, "[BOT] ", "bot", "orange")

    def __init__(self, id, prefix, rolename, color):
        self.id = id
        self.prefix = prefix
        self.rolename = rolename
        self.color = color
    
    def __str__(self):
        return f"Role(id={self.id}, prefix={self.prefix}, name={self.rolename})"

class Message:
    role: Role = None
    content: str = None

    def __init__(self, role: Role, content: str):
        self.role = role
        self.content = content
    
    def to_str(self):
        return f"{self.role.prefix}{self.content}"
    def __str__(self):
        return self.to_str()
    def __repr__(self):
        return self.to_str()

class Conversation():
    msgs:List[Message] = []
    
    def __init__(self):
        self.msgs = []

    def add_message(self, msg: Message):
        assert isinstance(msg, Message), f"Must be Message! But got {type(msg)}"
        self.msgs.append(msg)

    @classmethod
    def load_from_json(cls, o:List):
        instance = cls()
        for msg in o:
            if msg["role"] == "SYSTEM":
                _role = Role.SYSTEM
            elif msg["role"] == "USER":
                _role = Role.USER
            elif msg["role"] == "BOT":
                _role = Role.BOT
            else:
                raise ValueError(f"Unknown role: {msg['role']}")
            instance.add_message(Message(_role, msg["content"]))
        return instance

    def to_str(self):
        return "\n".join([msg.to_str() for msg in self.msgs])
    
    def copy(self):
        return copy.deepcopy(self)
    
    def __add__(self, other):
        if type(other) == list:
            assert isinstance(other[0], Message), f"Must be list of Message!"
            self.msgs += other
        elif isinstance(other, Conversation):
            self.msgs += other.msgs
        else:
            raise NotImplementedError
        return self
    
    def __str__(self):
        return self.to_str()
    def __repr__(self):
        return self.to_str()

@dataclass
class Config:
    workflow_dir: str = DIR_huabu_step3
    workflow_name: str = "xxx"
    model_name: str = "qwen2_72B"
    template_fn: str = "query_PDL.jinja"
    api_mode: str = "v01"
    api_model_name: str = "gpt-4o-mini"
    user_mode: str = "manual"
    user_model_name: str = "gpt-4o-mini"
    
    @classmethod
    def from_yaml(cls, yaml_file: str, normalize: bool = True):
        # DONE: read config file
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        obj = cls(**data)
        if normalize: obj.normalize_paths()
        return obj
    
    def normalize_paths(self):
        self.workflow_dir = DataManager.normalize_workflow_dir(self.workflow_dir)
        self.workflow_name = DataManager.normalize_workflow_name(self.workflow_name, self.workflow_dir)
        return self
    
    def __repr__(self):
        return str(asdict(self))
    def to_dict(self):
        return asdict(self)
    def copy(self):
        return Config(**self.to_dict())


@dataclass
class ConversationInfos:
    previous_action_type: ActionType = None
    num_user_query: int = 0
    
    @classmethod
    def from_components(cls, previous_action_type, num_user_query):
        return cls(previous_action_type, num_user_query)

@dataclass
class ConversationHeaderInfos:
    workflow_name: str = ""
    model_name: str = ""
    start_time: str = ""
    # "template_fn": self.bot.template_fn,
    # "workflow_dir": self.workflow_dir,
    # "log_file": self.logger.log_fn,

    @classmethod
    def from_components(cls, workflow_name, model_name):
        return cls(
            workflow_name, model_name, 
            start_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )



class BaseRole:
    def process(self, conversation:Conversation=None, pdl:PDL=None, *args, **kwargs) -> Tuple[ActionType, Dict, Message]:
        """ 
        return:
            action_type, action_metas, msg
        """
        raise NotImplementedError

