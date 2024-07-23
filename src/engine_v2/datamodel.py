""" 
@240712
"""
import datetime, os, re, yaml
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from colorama import init, Fore, Style

from .pdl import PDL
from .common import DIR_huabu_step3, DataManager

from engine_v1.datamodel import Role, Message, ActionType, Conversation

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
    def process(self, conversation:Conversation=None, pdl:PDL=None, *args, **kwargs):
        raise NotImplementedError

