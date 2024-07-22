from typing import List, Dict, Optional, Tuple

from .pdl import PDL

class PDLNode:
    name: str
    precondition: List[str] = []
    is_activated: bool = False
    # is_end: bool = False
    
    def __init__(self, name:str, preconditions:str=None) -> None:
        self.name = name
        if preconditions is not None:
            self.precondition = self._parse_preconditions(preconditions)

    def _parse_preconditions(self, s:str) -> List[str]:
        s = s.strip().lstrip("[").rstrip("]")
        names = s.split(",")
        return [n.strip() for n in names]

    def __repr__(self) -> str:
        return f"PDLNode({self.name}, {self.precondition})"
    def __str__(self) -> str:
        return f"PDLNode({self.name})"


class PDLGraph:
    # nodes: List[PDLNode] = []
    name2node: Dict[str, PDLNode] = {}
    
    def add_node(self, node:PDLNode):
        assert node.name not in self.name2node, f"node {node.name} already exists!"
        self.name2node[node.name] = node
    
    def check_preconditions(self) -> bool:
        names = self.name2node.keys()
        for node in self.name2node.values():
            for name in node.precondition:
                assert name in names, f"precondition {name} not found in nodes: {names}!!"
        return True
    
    def __repr__(self) -> str:
        return f"PDLGraph({self.name2node})"


class PDLController:
    pdl: PDL = None
    graph: PDLGraph = None
    curr_node = None
    
    def __init__(self, pdl:PDL) -> None:
        self.pdl = pdl
        self.graph = self.build_graph(pdl)
    
    def build_graph(self, pdl:PDL):
        apis = pdl.apis
        g = PDLGraph()
        for api in apis:
            g.add_node(PDLNode(api["name"], api.get("precondition", None)))
        g.check_preconditions()
        return g
    
    def check_validation(self, next_node:str) -> Tuple[bool, str]:
        node = self.graph.name2node[next_node]
        if node.precondition:
            for p in node.precondition:
                if not self.graph.name2node[p].is_activated:
                    msg = f"Precondition check failed! {p} not activated for {next_node}!"
                    # print(f"<debug> {msg}")
                    return False, msg
        node.is_activated = True
        msg = f"Check success! {next_node} activated!"
        # print(f"<debug> {msg}")
        return True, msg

