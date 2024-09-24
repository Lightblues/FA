""" updated @240906
InputUser: interact manually
LLMSimulatedUserWithProfile
"""
import re
from typing import List
from .base import BaseUser
from ..data import UserOutput, UserProfile, Role, Message, LogUtils, init_client, LLM_CFG
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater


class DummyUser(BaseUser):
    names: List[str] = ["dummy_user"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        
    def process(self, *args, **kwargs) -> UserOutput:
        """ 
        1. generate user query (free style?)
        """
        self.conv.add_message(
            Message(role=Role.USER, content="user query..."),
        )
        return UserOutput()


class InputUser(BaseUser):
    names = ["manual", "input_user", "InputUser"]
    
    def process(self, *args, **kwargs) -> UserOutput:
        user_input = ""
        while not user_input.strip():
            user_input = LogUtils.format_user_input("[USER] ")
        self.conv.add_message(
            Message(Role.USER, user_input)
        )
        return UserOutput(response_content=user_input.strip())


class LLMSimulatedUserWithProfile(BaseUser):
    user_profile: UserProfile = None
    names = ["llm_profile", "LLMSimulatedUserWithProfile"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.user_llm_name])
        assert self.cfg.user_profile is not None and self.cfg.user_profile_id is not None, "cfg.user_profile or cfg.user_profile_id is None!"
        self.user_profile = self.workflow.user_profiles[self.cfg.user_profile_id]

    def process(self, *args, **kwargs) -> UserOutput:
        prompt = jinja_render(
            self.cfg.user_template_fn,  # "flowagent/user_llm.jinja": assistant_description, user_profile, history_conversation
            assistant_description=self.workflow.task_description,
            user_profile=self.user_profile.to_str(),
            history_conversation=self.conv.to_str()
        )
        llm_response = self.llm.query_one(prompt)
        # ...parse the response! -> UserOutput, conv
        prediction = self.parse_user_output(llm_response)
        msg = Message(
            Role.USER, prediction.response_content, prompt=prompt, llm_response=llm_response,
            conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
        )
        self.conv.add_message(msg)
        self.cnt_user_queries += 1  # stat
        return prediction
    
    @staticmethod
    def parse_user_output(s: str) -> UserOutput:
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(Response):\s*(.*?)(?=\n\w+:|\Z)"
        matches = re.findall(pattern, s, re.DOTALL)
        if not matches:
            response = s
        else:
            result = {key: value.strip() for key, value in matches}
            assert UserOutput.response_str in result, f"Response not in prediction: {s}"
            response = result[UserOutput.response_str]
        return UserOutput(response_content=response)