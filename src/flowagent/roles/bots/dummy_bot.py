"""updated 240924
- [x] add pdl bot
    - [ ] check performance diff for JSON / React output
- [ ] add lke bot?
"""

from typing import List

from data import BotOutput, Message, Role

from ..base import BaseBot


class DummyBot(BaseBot):
    names: List[str] = ["dummy_bot"]
    bot_template_fn: str = ""

    # def __init__(self, **args) -> None:
    #     super().__init__(**args)

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
