from typing import Dict, List, Tuple

from pydantic import Field

from data import PDL, BotOutput

from .base_controller import BaseController
from .pdl_utils import PDLGraph, PDLNode


class NodeDependencyController(BaseController):
    """Dependency controller (with DAG)

    Variables:
        graph, pdl

    Usage::

        cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
        workflow = Workflow(cfg)
        conv = Conversation()

        controller = NodeDependencyController(conv=conv, pdl=workflow.pdl, config={"if_pre": True, "if_post": True, "threshold": 2})

        bot_output: BotOutput = BotOutput(action="check_hospital", action_input={"hospital_name": "test"}, response=None)
        res = controller.post_control(bot_output)
        print(f">>> post_control: {res}")

        controller.pre_control(bot_output)
        print(f">>> pre_control: {controller.pdl.status_for_prompt}")
    """

    names = ["node_dependency"]

    graph: PDLGraph = None
    # curr_node = None  # ... to be used?

    if_add_invalid_msg: bool = True
    if_add_valid_msg: bool = False

    def _post_init(self) -> None:
        self.graph = PDLGraph.from_pdl(self.context.data_handler.pdl)

    # def refresh_pdl(self, pdl: PDL):
    #     super().refresh_pdl(pdl)
    #     self.graph = self._build_graph(pdl)

    def _post_check_with_message(self, bot_output: BotOutput) -> Tuple[bool, str]:
        """Check if the next action is valid (all the preconditions are satisfied)"""
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
        """Update the status for prompt"""
        all_api_names = {api.name for api in self.context.data_handler.pdl.APIs}
        invalid_apis = self.graph.get_invalid_node_names()
        valid_apis = all_api_names - invalid_apis
        if self.if_add_invalid_msg and (len(invalid_apis) > 0):
            self.context.status_for_prompt["Current invalid apis"] = (
                f"`{invalid_apis}` are invalid because the precondintion APIs have not been called!"
            )
        if self.if_add_valid_msg and (len(valid_apis) > 0):
            self.context.status_for_prompt["Current valid apis"] = f"You can call `{valid_apis}`"
