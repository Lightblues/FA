""" updated @240905
InputUser: interact manually
LLMSimulatedUserWithProfile
"""

from typing import List
from .base import BaseUser
from .user_profile import UserProfile
from ..data import UserOutput
from engine import Role, Message, prompt_user_input
from utils.jinja_templates import jinja_render


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
        user_input = prompt_user_input("[USER] ")       # user_input_prefix, user_color
        while not user_input.strip():
            user_input = prompt_user_input("[USER] ")
        self.conv.add_message(
            Message(Role.USER, user_input)
        )
        return UserOutput()


class LLMSimulatedUserWithProfile(BaseUser):
    user_profile: UserProfile
    names = ["llm_profile", "LLMSimulatedUserWithProfile"]
    
    def __init__(self, user_profile:UserProfile=None, **args) -> None:
        super().__init__(**args)
        self.user_profile = user_profile
    
    def load_user_profile(self, user_profile:UserProfile):
        self.user_profile = user_profile

    def process(self, *args, **kwargs) -> UserOutput:
        """ 根据当前的会话进度, 扮演用户角色, 生成下一轮query 
        TODO: prompting!
        """
        assert self.user_profile is not None, "user_profile is None!"
        # user_output = UserOutput()
        
        prompt = jinja_render(
            "user_role_player.jinja",
            # assistant_description=assistant_desc,
            # user_information=self.user_profile.to_str(),
            # conversation=conversation.to_str()
        )
        llm_response = self.llm.query_one(prompt)
        self.conv.add_message(
            Message(role=Role.USER, content=llm_response),
        )
        return UserOutput()