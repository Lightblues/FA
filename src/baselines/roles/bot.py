""" updated 240905
"""

from typing import List
from engine import Message, Role
from .base import BaseBot
from ..common import BotOutput, BotOutputType

class DummyBot(BaseBot):
    names: List[str] = ["dummy_bot"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.cnt_bot_actions: int = 0

    def process(self, *args, **kwargs) -> BotOutput:
        """ 
        1. generate ReAct format output by LLM
        2. parse to BotOutput
        """
        self.cnt_bot_actions += 1
        
        if (self.cnt_bot_actions % 2) == 0:
            bot_output = BotOutput(action="calling api!")
            self.conv.add_message(
                Message(role=Role.BOT, content="bot action..."),
            )
        else:
            bot_output = BotOutput(response="bot response...")
            self.conv.add_message(
                Message(role=Role.BOT, content="bot response..."),
            )
        return bot_output