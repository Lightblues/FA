import abc
from typing import Tuple, List, Dict
from ..data import PDL, Conversation, Role, Message, Config, BotOutput


class BaseController:
    """ abstraction class for action checkers 
    """
    cfg: Config = None
    conv: Conversation = None
    pdl: PDL = None
    config: Dict = None
    
    name: str = ""      # to build CONTROLLER_NAME2CLASS
    if_post_check = False
    if_pre_check = False
    
    def __init__(self, cfg: Config, conv:Conversation, pdl: PDL, config: Dict, *args, **kwargs) -> None:
        self.cfg = cfg
        self.conv = conv        # the conversation! update it when necessary!
        self.pdl = pdl
        self.config = config
        if "if_post" in config: self.if_post_check = config["if_post"]
        if "if_pre" in config: self.if_pre_check = config["if_pre"]
        assert self.if_post_check or self.if_pre_check, "at least one of if_post_check or if_pre_check should be True"

    def post_check(self, bot_output: BotOutput) -> bool:
        """ standard process:
        post: check validation, if not validated, log the error info to self.conv!
        pre: make modifications on `PDL.status_for_prompt` -> change the bot's prompt!
        """
        assert self.if_post_check, "if_post_check should be True"
        res, msg_content = self._post_check_with_message(bot_output)
        if not res:
            msg = Message(
                Role.SYSTEM, msg_content, prompt="", llm_response="",
                conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
            )
            self.conv.add_message(msg)
        return res
    
    def pre_control(self, prev_bot_output: BotOutput):
        assert self.if_pre_check, "if_pre_check should be True"
        self._pre_control(prev_bot_output)

    @abc.abstractmethod
    def _post_check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        raise NotImplementedError
    
    @abc.abstractmethod
    def _pre_control(self, prev_bot_output: BotOutput):
        raise NotImplementedError

