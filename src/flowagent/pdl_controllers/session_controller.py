from typing import Tuple

from ..data import BotOutput, BotOutputType, Role
from .base_controller import BaseController


class SessionLengthController(BaseController):
    """ """

    name = "session_length"
    if_response_control = False  # default value, can be overwritten in config
    if_pre_control = True

    def _pre_control(self, prev_bot_output: BotOutput):
        num_user_queries = self.get_num_user_queries()
        msg = None
        if num_user_queries < self.config["min"]:
            msg = f"Current #user_queries = {num_user_queries} is less than minimum ({self.config['min']}). Keep chatting with the user!"
        elif num_user_queries > self.config["max"]:
            msg = f"Current #user_queries = {num_user_queries} is greater than maximum ({self.config['max']}). Try to stop the conversation soon!"
        if msg:
            self.pdl.status_for_prompt["Session length"] = msg

    def _response_check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        # FIXME: check only when the bot say "byebye"
        assert bot_output.action_type == BotOutputType.RESPONSE
        num_user_queries = self.get_num_user_queries()
        if num_user_queries < self.config["min"]:
            return False, f"num_user_queries < {self.config['min']}"
        if num_user_queries > self.config["max"]:
            return False, f"num_user_queries > {self.config['max']}"
        return True, ""

    def get_num_user_queries(self) -> int:
        return self.conv.get_messages_num(Role.USER)
