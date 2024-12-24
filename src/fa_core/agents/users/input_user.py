from typing import List

from fa_core.common import LogUtils
from fa_core.data import Message, Role, UserOutput

from .base_user import BaseUser


class InputUser(BaseUser):
    names = ["manual", "input_user", "InputUser"]
    user_template_fn: str = ""

    def process(self, *args, **kwargs) -> UserOutput:
        user_input = ""
        while not user_input.strip():
            user_input = LogUtils.format_user_input("[USER] ")
        self.conv.add_message(
            Message(
                Role.USER,
                user_input,
                conversation_id=self.conv.conversation_id,
                utterance_id=self.conv.current_utterance_id,
            )
        )
        return UserOutput(response_content=user_input.strip())
