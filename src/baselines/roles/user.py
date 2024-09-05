from typing import List
from .base import BaseUser
from ..common import UserOutput
from engine import Role, Message


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