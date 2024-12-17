from typing import Tuple, Union

from ..data import BotOutput, Role
from .base_controller import BaseController


class APIDuplicationController(BaseController):
    """to avoid duplicated API calls!"""

    name = "api_duplication"
    if_post_control = True  # default value, can be overwritten in config

    def _post_check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        res = self.check_validation()
        msg = "Check success!" if res else f"Too many duplicated API calls! try another action instead."
        return res, msg

    def _pre_control(self, prev_bot_output: Union[BotOutput, None]):
        # if not isinstance(prev_bot_output, BotOutput): return  # TODO:
        if prev_bot_output is None:
            return
        if not (prev_bot_output.action):
            return
        if not self.check_validation():
            content = f"you have called {prev_bot_output.action} with the same parameters too many times! Please obtain the information from the previous calls."
            self.pdl.status_for_prompt["Invalid API due to duplicated call"] = content

    def check_validation(self) -> bool:
        app_calling_info = self.conv.get_last_message().content
        duplicate_cnt = 0
        for check_idx in range(len(self.conv) - 1, -1, -1):
            previous_msg = self.conv.get_message_by_idx(check_idx)
            if previous_msg.role != Role.BOT:
                continue
            if previous_msg.content != app_calling_info:
                break
            duplicate_cnt += 1
            if duplicate_cnt > self.config["threshold"]:
                return False
        return True
