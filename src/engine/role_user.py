""" 

@240723 
"""
import traceback
from typing import List, Dict, Optional

from .datamodel import BaseRole, Config
from .common import prompt_user_input, init_client, LLM_CFG
from .datamodel import Message, Conversation, Role, ActionType
from .pdl import PDL
from .user_profile import UserProfile
from easonsi.llm.openai_client import OpenAIClient, Formater
from utils.jinja_templates import jinja_render


def handle_exceptions(func=None, default_response="..."):
    """ 异常捕获, 返回错误信息 -> for simulateing user!
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # print(e)
            print(traceback.format_exc())
            return default_response
    return wrapper


class BaseUser(BaseRole):
    llm: OpenAIClient = None
    cfg: Config = None
    names: List[str] = []                   # for convert name2role
    
    def __init__(self, cfg:Config) -> None:
        super().__init__()
        self.cfg = cfg
        if cfg.user_mode not in ["manual"]:
            self.llm = init_client(llm_cfg=LLM_CFG[cfg.user_model_name])

    @handle_exceptions
    def process_llm_response(self, llm_response:str) -> str:
        parsed_response = Formater.parse_llm_output_json(llm_response)
        content = parsed_response["content"]
        return content


class InputUser(BaseRole):
    names = ["manumal", "InputUser"]
    def process(self, **kwargs):
        """ User that manually input!  """
        action_metas = {}
        user_input = prompt_user_input("[USER] ")       # user_input_prefix, user_color
        while not user_input.strip():
            user_input = prompt_user_input("[USER] ")
        msg = Message(Role.USER, user_input)
        return ActionType.USER_INPUT, action_metas, msg


class LLMSimulatedUserWithRefConversation(BaseUser):
    ref_conversation: Conversation
    names = ["llm_ref", "LLMSimulatedUserWithRefConversation"]
    
    def __init__(self, cfg:Config, ref_conversation:Conversation=None) -> None:
        super().__init__(cfg=cfg)
        self.ref_conversation = ref_conversation

    def load_ref_conversation(self, ref_conversation:Conversation):
        self.ref_conversation = ref_conversation

    def process(self, conversation:Conversation, **kwargs):
        """ 根据当前的会话进度, 生成下一轮query """
        assert self.ref_conversation is not None, "ref_conversation is None!"
        action_metas = {}
        
        prompt = jinja_render( # TODO: optimize the prompt
            "user_simulator.jinja",
            ref_conversation=self.ref_conversation.to_str(),
            new_conversation=conversation.to_str(),
        )
        llm_response = self.llm.query_one(prompt)
        action_metas.update(prompt=prompt, llm_response=llm_response)       # for debug
        
        msg = Message(Role.USER, self.process_llm_response(llm_response))
        return ActionType.USER_INPUT, action_metas, msg


class LLMSimulatedUserWithProfile(BaseUser):
    user_profile: UserProfile
    names = ["llm_profile", "LLMSimulatedUserWithProfile"]
    
    def __init__(self, cfg:Config, user_profile:UserProfile=None) -> None:
        super().__init__(cfg=cfg)
        self.user_profile = user_profile
    
    def load_user_profile(self, user_profile:UserProfile):
        self.user_profile = user_profile
    
    def process(self, conversation:Conversation, pdl: PDL, **kwargs):
        """ 根据当前的会话进度, 扮演用户角色, 生成下一轮query """
        assert self.user_profile is not None, "user_profile is None!"
        action_metas = {}
        
        # 构造助手描述信息："{{ taskflow_name }}机器人。{{ taskflow_desc }}"
        assistant_desc = f"{pdl.taskflow_name}机器人。{pdl.taskflow_desc}"
        # 模型扮演
        prompt = jinja_render(
            "user_role_player.jinja",
            assistant_description=assistant_desc,
            user_information=self.user_profile.to_str(),
            conversation=conversation.to_str()
        )
        print(prompt)
        llm_response = self.llm.query_one(prompt)
        action_metas.update(prompt=prompt, llm_response=llm_response)

        msg = Message(Role.USER, self.process_llm_response(llm_response))
        return ActionType.USER_INPUT, action_metas, msg


USER_NAME2CLASS:Dict[str, BaseUser] = {}
for cls in BaseUser.__subclasses__():
    for name in cls.names:
        USER_NAME2CLASS[name] = cls
    