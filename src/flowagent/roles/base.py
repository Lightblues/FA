import collections
from abc import abstractmethod
from typing import Dict, Iterator, List, Tuple, Union

from common import LLM_CFG, Config, OpenAIClient, init_client
from data import (
    APIOutput,
    BotOutput,
    Conversation,
    DataHandler,
    UserOutput,
)


class BaseRole:
    names: List[str] = None  # for convert name2role
    cfg: Config = None  # unified config
    llm: OpenAIClient = None  # for simulation
    conv: Conversation = None  # global variable for conversation
    workflow: DataHandler = None

    def __init__(
        self,
        cfg: Config,
        conv: Conversation = None,
        workflow: DataHandler = None,
        *args,
        **kwargs,
    ) -> None:
        self.cfg = cfg
        self.conv = conv
        self.workflow = workflow

    @abstractmethod
    def process(self, *args, **kwargs) -> Union[UserOutput, BotOutput, APIOutput]:
        """
        return:
            action_type, action_metas, msg
        """
        raise NotImplementedError
