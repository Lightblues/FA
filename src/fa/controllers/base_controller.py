import abc
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import BaseModel, Field

from common import Config
from data import PDL, BotOutput, Conversation, Role
from fa.envs import Context


class BaseController(BaseModel):
    """abstraction class for action checkers"""

    names: ClassVar[List[str]] = []  # to build CONTROLLER_NAME2CLASS

    config: Dict = None
    context: Context = Field(default=None)  # , exclude=True)  # NOTE: avoid circular import

    is_activated: bool = True  # can be disabled
    if_pre_control: bool = False
    if_post_control: bool = True
    # if_response_control: bool = False

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        config = self.config
        assert self.if_post_control or self.if_pre_control, "at least one of if_post_control or if_pre_control should be True"
        if "if_post" in config:
            self.if_post_control = config["if_post"]
        if "if_pre" in config:
            self.if_pre_control = config["if_pre"]
        # if "if_response" in config: self.if_response_control = config["if_response"]
        self._post_init()

    def _post_init(self) -> None:
        """e.g. init the llm"""
        pass

    # def refresh_pdl(self, pdl: PDL):
    #     self.pdl = pdl

    """ standard processes:
    pre_control: make modifications on `PDL.status_for_prompt` -> change the bot's prompt!
    post_control: check validation, if not validated, log the error info to self.conv!
    response_control: similar to post_control
    """

    def pre_control(self, prev_bot_output: BotOutput) -> bool:
        if not self.is_activated:
            return True
        assert self.if_pre_control, "if_pre_control should be True"
        self._pre_control(prev_bot_output)

    def post_control(self, bot_output: BotOutput) -> bool:
        if not self.is_activated:
            return True
        assert self.if_post_control, "if_post_control should be True"
        res, msg_content = self._post_check_with_message(bot_output)
        # print(f">>> {self.name} post_control: {res} {msg_content}")
        if not res:
            self.context.conv.add_message(msg_content, role=Role.SYSTEM)
        return res

    # def response_control(self, bot_output: BotOutput) -> bool:
    #     if not self.is_activated:
    #         return True
    #     assert self.if_response_control, "if_response_control should be True"
    #     res, msg_content = self._response_check_with_message(bot_output)
    #     if not res:
    #         self.context.conv.add_message(msg_content, role=Role.SYSTEM)
    #     return res

    @abc.abstractmethod
    def _pre_control(self, prev_bot_output: BotOutput):
        raise NotImplementedError

    @abc.abstractmethod
    def _post_check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        raise NotImplementedError

    # @abc.abstractmethod
    # def _response_check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
    #     raise NotImplementedError
