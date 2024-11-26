
from typing import Tuple, List
from .base_controller import BaseController
from ..data import PDL, Conversation, Role, Message, Config, BotOutput
from .pdl_utils import PDLNode, PDLGraph


class NodeDependencyController(BaseController):
    """Dependency controller (with DAG)

    Variables:
        graph, pdl

    Usage::
    
        cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
        workflow = Workflow(cfg)
        conv = Conversation()
        
        controller = NodeDependencyController(conv=conv, pdl=workflow.pdl, 
            config={"if_pre": True, "if_post": True, "threshold": 2})

        bot_output: BotOutput = BotOutput(action="check_hospital", action_input={"hospital_name": "test"}, response=None)
        res = controller.post_control(bot_output)
        print(f">>> post_control: {res}")

        controller.pre_control(bot_output)
        print(f">>> pre_control: {controller.pdl.status_for_prompt}")
    """
    name = "node_dependency"
    
    graph: PDLGraph = None
    curr_node = None                # ... to be used?
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.graph = self._build_graph(self.pdl)
    
    def refresh_pdl(self, pdl: PDL):
        super().refresh_pdl(pdl)
        self.graph = self._build_graph(pdl)
    
    def _build_graph(self, pdl:PDL):
        if (pdl.apis is None) or (not pdl.apis):  # if pdl.apis is None
            pdl.apis = []
        apis = pdl.apis
        g = PDLGraph()
        for api in apis:
            node = PDLNode(name=api["name"], preconditions=api.get("precondition", None))
            g.add_node(node)
        g.check_preconditions()
        return g

    def _post_check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
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
    
    def _pre_control(self, prev_bot_output: BotOutput):
        # 我这里先重置一下, 直接在这个controller里面修改
        self.pdl.reset_invalid_api(); self.pdl.reset_api_status()
        # check the dependencies of next turn, and reset the invalid API list
        next_turn_invalid_apis = self.graph.get_invalid_node_names()
        if len(next_turn_invalid_apis) > 0:
            self.pdl.add_invalid_apis(self._add_invalid_reason(next_turn_invalid_apis, "API dependency not satisfied: The precondintion API has not been called."))
            self.pdl.add_current_api_status(self._get_invalid_status_str(next_turn_invalid_apis, "API dependency not satisfied: The precondintion API has not been called."))

        # set the pdl.status_for_prompt dict -> for PDLBot's prompt
        # 1. Current valid apis
        valid_apis = self.pdl.get_valid_apis()
        valid_api_names = [api["name"] for api in valid_apis]
        valid_apis_str = "There are no valid apis now!" if not valid_apis else f"You can call `{valid_api_names}`"
        self.pdl.status_for_prompt["Current valid apis"] = valid_apis_str
        # 2. Current state
        self.pdl.status_for_prompt["Current state"] = self.pdl.current_api_status

    def _add_invalid_reason(self, api_names: List[str], msg: str):
        apis_w_reason = [{"api_name": api_name, "invalid_reason": [msg]} for api_name in api_names]
        return apis_w_reason
    
    def _get_invalid_status_str(self, api_names: List[str], msg: str):
        return f"APIs `{api_names}` is unavailable. Reason: {msg}"
