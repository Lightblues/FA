""" Graph structure of PDL & Graph-based Dependency Controller

@240718 节点抽象、PDLController 控制逻辑
"""
import json
from typing import List, Dict, Optional, Tuple

from .pdl import PDL

class PDLNode:
    name: str
    precondition: List[str] = []
    is_activated: bool = False
    # is_end: bool = False
    version: str = "v1"
    
    def __init__(self, name:str, preconditions:str=None, version:str=None) -> None:
        self.name = name
        if version: self.version = version
        if preconditions is not None:
            if self.version == "v1":
                self.precondition = self._parse_preconditions(preconditions)
            elif self.version == "v2":
                assert isinstance(preconditions, list)
            else: raise Exception(f"unknown version {self.version}")
        

    def _parse_preconditions(self, s:str) -> List[str]:
        try:
            preconditions = eval(s)
        except Exception as e:
            s = s.strip().lstrip("[").rstrip("]")
            names = s.split(",")
            preconditions = []
            for s in names:
                s = s.strip('\'').strip('\"').strip()
                if s: preconditions.append(s)
        return preconditions

    def __repr__(self) -> str:
        return f"PDLNode({self.name}, {self.precondition})"
    def __str__(self) -> str:
        return f"PDLNode({self.name})"


class PDLGraph:
    # nodes: List[PDLNode] = []
    name2node: Dict[str, PDLNode] = {}
    version: str = "v1"
    
    def __init__(self, version:str=None) -> None:
        self.name2node = {}     # NOTE: have to add __init__ to clear the dict
        if version: self.version = version
    
    def add_node(self, node:PDLNode):
        assert node.name not in self.name2node, f"node {node.name} already exists!"
        self.name2node[node.name] = node
    
    def check_preconditions(self) -> bool:
        names = set(self.name2node.keys())
        for node in self.name2node.values():
            for name in node.precondition:
                if not name: continue
                assert name in names, f"precondition `{name}` not found in nodes: {names}!!"
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
            g.add_node(PDLNode(api["name"], api.get("precondition", None), pdl.version))
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

