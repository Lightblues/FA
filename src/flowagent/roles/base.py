import collections
from abc import abstractmethod
from typing import List, Dict, Optional, Tuple, Union
from ..utils import OpenAIClient, init_client, LLM_CFG
from ..data import (
    Config, UserOutput, BotOutput, APIOutput, BotOutputType,
    Conversation, Workflow, Role, Message
)


class BaseRole:
    names: List[str] = None         # for convert name2role
    cfg: Config = None              # unified config
    llm: OpenAIClient = None        # for simulation
    conv: Conversation = None       # global variable for conversation
    workflow: Workflow = None
    
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


class BaseTool(BaseRole):
    """ 
    API structure: (see apis_v0/apis.json)
    """
    names: List[str] = None
    api_infos: List[Dict] = None
    cnt_api_callings: Dict[str, int] = None
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.api_infos = self.workflow.toolbox
        self.cnt_api_callings = collections.defaultdict(int)
        
    def process(self, *args, **kwargs) -> APIOutput:
        """ 
        1. match and check the validity of API
        2. call the API (with retry?)
        3. parse the response
        """
        raise NotImplementedError


class BaseBot(BaseRole):
    names: List[str] = None
    bot_template_fn: str = ""
    cnt_bot_actions: int = None
    llm: OpenAIClient = None
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.cnt_bot_actions: int = 0
        # overwrite the default template
        if self.cfg.bot_template_fn is not None: self.bot_template_fn = self.cfg.bot_template_fn
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.bot_llm_name])

    def process(self, *args, **kwargs) -> BotOutput:
        """ 
        1. generate ReAct format output by LLM
        2. parse to BotOutput
        """
        raise NotImplementedError

    def process_stream(self):
        prompt = self._gen_prompt()
        llm_response_stream = self.llm.query_one_stream_generator(prompt)
        return prompt, llm_response_stream


class BaseUser(BaseRole):
    names: List[str] = None     # for convert name2role
    user_template_fn: str = ""  # for get LLM prompt
    cnt_user_queries: int = None
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.cnt_user_queries: int = 0
        # overwrite the default template
        if self.cfg.user_template_fn is not None: self.user_template_fn = self.cfg.user_template_fn
    
    def process(self, *args, **kwargs) -> UserOutput:
        """ 
        1. generate user query (free style?)
        """
        raise NotImplementedError
