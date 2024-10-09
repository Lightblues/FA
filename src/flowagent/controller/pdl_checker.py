import abc
from typing import Tuple, List
from ..data import PDL, Conversation, Role, Message, Config, BotOutput
from .pdl_utils import PDLNode, PDLGraph


class BaseChecker:
    """ abstraction class for action checkers 
    USAGE:
        checker = XXXChecker(cfg, conv)
        res = checker.check(bot_output)
    """
    cfg: Config = None
    conv: Conversation = None
    pdl: PDL = None
    
    def __init__(self, cfg: Config, conv:Conversation, pdl: PDL, *args, **kwargs) -> None:
        self.cfg = cfg
        self.conv = conv        # the conversation! update it when necessary!
        self.pdl = pdl

    def check(self, bot_output: BotOutput) -> bool:
        # 1. check validation
        res, msg_content = self._check_with_message(bot_output)
        # 2. if not validated, log the error info!
        if not res:
            if not self.cfg.pdl_check_api_w_tool_manipulation:
                msg = Message(
                    Role.SYSTEM, msg_content, prompt="", llm_response="",
                    conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
                )
                self.conv.add_message(msg)
            else:
                self.pdl.add_invalid_apis(self.add_invalid_reason([bot_output.action], msg_content))
                self.pdl.add_current_api_status(self._get_invalid_status_str([bot_output.action], msg_content))
        return res
    
    def add_invalid_reason(self, api_names: List[str], msg: str):
        apis_w_reason = [{"api_name": api_name, "invalid_reason": [msg]} for api_name in api_names]
        return apis_w_reason
    
    @abc.abstractmethod
    def _get_invalid_status_str(self, api_names: List[str], msg: str):
        raise NotImplementedError

    @abc.abstractmethod
    def _check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        raise NotImplementedError


class PDLDependencyChecker(BaseChecker):
    pdl: PDL = None
    graph: PDLGraph = None
    curr_node = None
    
    def __init__(self, cfg:Config, conv:Conversation, pdl:PDL) -> None:
        super().__init__(cfg, conv, pdl)
        self.pdl = pdl
        self.graph = self._build_graph(pdl)
        # set initial API list, if checking the API call with tool manipulation
        if self.cfg.pdl_check_api_w_tool_manipulation:
            self.check_next_turn_dependencies()
    
    def _build_graph(self, pdl:PDL):
        if (pdl.apis is None) or (not pdl.apis):  # if pdl.apis is None
            pdl.apis = []
        apis = pdl.apis
        g = PDLGraph()
        for api in apis:
            node = PDLNode(name=api["name"], preconditions=api.get("precondition", None), version=pdl.version)
            g.add_node(node)
        g.check_preconditions()
        return g

    def _check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        next_node = bot_output.action
        # 1. match the node
        if next_node not in self.graph.name2node:
            return False, f"ERROR! Node {next_node} not found!"
        node = self.graph.name2node[next_node]
        # 2. check preconditions
        if node.precondition:
            for p in node.precondition:
                if not self.graph.name2node[p].is_activated:
                    msg = f"Precondition check failed! {p} not activated for {next_node}!"
                    return False, msg
        # 3. success! set it as activated
        node.is_activated = True
        msg = f"Check success! {next_node} activated!"
        return True, msg
    
    def check_next_turn_dependencies(self):
        # check the dependencies of next turn, and reset the invalid API list
        next_turn_invalid_apis = self.graph.get_invalid_node_names()
        if len(next_turn_invalid_apis) > 0:
            self.pdl.add_invalid_apis(self.add_invalid_reason(next_turn_invalid_apis, "API dependency not satisfied: The precondintion API has not been called."))
            self.pdl.add_current_api_status(self._get_invalid_status_str(next_turn_invalid_apis, "API dependency not satisfied: The precondintion API has not been called."))
        
    def _get_invalid_status_str(self, api_names: List[str], msg: str):
        return f"APIs `{api_names}` is unavailable. Reason: {msg}"


class APIDuplicatedChecker(BaseChecker):
    """ to avoid duplicated API calls! """

    def _check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        app_calling_info = self.conv.get_last_message().content
        duplicate_cnt = 0
        for check_idx in range(len(self.conv)-1, -1, -1):
            previous_msg = self.conv.get_message_by_idx(check_idx)
            if previous_msg.role != Role.BOT: continue
            if previous_msg.content != app_calling_info: break
            duplicate_cnt += 1
            if duplicate_cnt >= self.cfg.pdl_check_api_dup_calls_threshold:
                msg = f"Too many duplicated API calls! try another action instead."
                return False, msg
        msg = "Check success!"
        return True, msg
    
    def _get_invalid_status_str(self, api_names: List[str], msg: str):
        return f"you have called {api_names[0]} with the same parameters too many times! Please obtain the information from the previous calls."
