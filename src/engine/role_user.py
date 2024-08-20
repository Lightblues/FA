""" 

@240723 
"""
import traceback
from typing import List, Dict, Optional

from .datamodel import BaseRole, Config
from .common import prompt_user_input, init_client, LLM_CFG
from .datamodel import Message, Conversation, Role, ActionType
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


class InputUser(BaseRole):
    def process(self, **kwargs):
        """ User that manually input!  """
        action_metas = {}
        user_input = prompt_user_input("[USER] ")       # user_input_prefix, user_color
        while not user_input.strip():
            user_input = prompt_user_input("[USER] ")
        msg = Message(Role.USER, user_input)
        return ActionType.USER_INPUT, action_metas, msg
    
class LLMSimulatedUserWithRefConversation(BaseRole):
    llm: OpenAIClient
    ref_conversation: Conversation
    
    def __init__(self, cfg:Config, ref_conversation:Conversation=None) -> None:
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.user_model_name])
        self.ref_conversation = ref_conversation

    def load_ref_conversation(self, ref_conversation:Conversation):
        self.ref_conversation = ref_conversation

    @handle_exceptions
    def process_llm_response(self, llm_response:str) -> str:
        parsed_response = Formater.parse_llm_output_json(llm_response)
        content = parsed_response["content"]
        return content

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

