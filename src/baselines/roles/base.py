from abc import abstractmethod
from typing import List, Dict, Optional, Tuple, Union
from easonsi.llm.openai_client import OpenAIClient
from engine import Conversation, Message, Role
from ..common import Config, UserOutput, BotOutput, APIOutput, BotOutputType
from ..data import Tool, Workflow


class BaseRole:
    names: List[str] = ["base_role"]           # for convert name2role
    cfg: Config = None              # unified config
    llm: OpenAIClient = None        # for simulation
    conv: Conversation = None       # global variable for conversation
    workflow:Workflow = None
    
    def __init__(self, cfg:Config, conv:Conversation=None, workflow:Workflow=None, *args, **kwargs) -> None:
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


class BaseAPIHandler(BaseRole):
    """ 
    API structure: (see apis_v0/apis.json)
    """
    names: List[str] = ["base_api"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.cnt_api_callings: int = 0
        
    def process(self, *args, **kwargs) -> APIOutput:
        """ 
        1. match and check the validity of API
        2. call the API (with retry?)
        3. parse the response
        """
        # raise NotImplementedError
        self.cnt_api_callings += 1
        
        self.conv.add_message(
            Message(role=Role.SYSTEM, content="api calling..."),
        )
        api_output = APIOutput()
        return api_output


class BaseBot(BaseRole):
    names: List[str] = ["base_bot"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        
    def process(self, *args, **kwargs) -> BotOutput:
        """ 
        1. generate ReAct format output by LLM
        2. parse to BotOutput
        """
        raise NotImplementedError


class BaseUser(BaseRole):
    names: List[str] = ["base_user"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        
    def process(self, *args, **kwargs) -> UserOutput:
        """ 
        1. generate user query (free style?)
        """
        raise NotImplementedError
