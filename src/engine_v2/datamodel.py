""" 
@240712
"""
import datetime, os, re, yaml
from enum import Enum, auto
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater

from engine_v1.datamodel import Role, Message, Conversation, PDL, ActionType
from engine_v1.common import LLM_stop, DIR_data, init_client, LLM_CFG
from utils.jinja_templates import jinja_render


@dataclass
class Config:
    workflow_dir: str = DIR_data
    workflow_name: str = "xxx"
    model_name: str = "qwen2_72B"
    template_fn: str = "query_PDL.jinja"
    
    @classmethod
    def from_yaml(cls, yaml_file: str):
        # DONE: read config file
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        return cls(**data)
    
    def __repr__(self):
        return str(asdict(self))


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



class Controller:
    def __init__(self):
        pass


class BaseRole:
    def process(self, conversation:Conversation, pdl:PDL, **kwargs):
        raise NotImplementedError

class InputUser(BaseRole):
    def process(self, **kwargs):
        """ User that manually input!  """
        user_input = input("[USER] ")       # user_input_prefix
        msg = Message(Role.USER, user_input)
        return ActionType.USER, None, msg
    

class ManualAPIHandler(BaseRole):
    def process(self, conversation:Conversation, paras:Dict, **kwargs):
        api_name, api_params = paras["action_name"], paras["action_parameters"]
        res = input(f"<manual> please fake the response of the API call {api_name}({api_params}): ")
        msg = Message(Role.SYSTEM, res)
        return ActionType.API_RESPONSE, None, msg


class PDLBot(BaseRole):
    llm: OpenAIClient = None
    cfg: Config = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.model_name])
    
    def process(self, conversation:Conversation, pdl:PDL, conversation_infos:ConversationInfos=None):
        """ 
        return:
            action_type: [ActionType.REQUEST, ActionType.ANSWER, ActionType.API]
            action_metas: Dict, return API parameters if action_type == ActionType.API
        """
        if conversation_infos is not None:
            s_current_state = f"Previous action type: {conversation_infos.previous_action_type}. The number of user queries: {conversation_infos.num_user_query}."
        else:
            s_current_state = None
        prompt = jinja_render(
            self.cfg.template_fn,       # "query_PDL.jinja"
            conversation=conversation.to_str(), 
            PDL=pdl.to_str(),
            current_state=s_current_state
        )
        llm_response = self.llm.query_one_stream(prompt)
        # _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<prompt>>\n{prompt}\n\n<<response>>\n{llm_response}\n"
        # self.logger.debug(_debug_msg)
        
        parsed_response = Formater.parse_llm_output_json(llm_response)
        
        # -> ActionType
        assert "action_type" in parsed_response, f"parsed_response: {parsed_response}"
        try:
            action_type = ActionType[parsed_response["action_type"]]
        except KeyError:
            raise ValueError(f"Unknown action_type: {parsed_response['action_type']}")
        # -> action_metas
        action_name, action_paras, response = parsed_response.get("action_name", "DEFTAULT_ACTION"), parsed_response.get("action_parameters", "DEFAULT_PARAS"), parsed_response.get("response", "DEFAULT_RESPONSE")
        action_metas = {"action_name": action_name, "action_parameters": action_paras}
        # -> msg
        if action_type == ActionType.API:
            msg = Message(Role.BOT, f"<Call API> {action_name}({action_paras})")        # bot_callapi_template
        else:
            msg = Message(Role.BOT, response)
        return action_type, action_metas, msg