""" Graph structure of PDL & Graph-based Dependency Controller
updated @240918

"""
from typing import List, Dict, Optional, Tuple
from ..data.pdl import PDL

class PDLNode:
    name: str
    precondition: List[str] = []
    is_activated: bool = False
    # is_end: bool = False
    
    def __init__(self, name:str, preconditions:str=None) -> None:
        self.name = name
        if preconditions is not None:
            assert isinstance(preconditions, list)
            self.precondition = preconditions

    def __repr__(self) -> str:
        return f"PDLNode({self.name}, with precondition {self.precondition})"
    # def __str__(self) -> str:
    #     return f"PDLNode({self.name})"


class PDLGraph:
    # nodes: List[PDLNode] = []
    name2node: Dict[str, PDLNode] = {}
    
    def __init__(self) -> None:
        self.name2node = {}     # NOTE: have to add __init__ to clear the dict
    
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
    
    def get_invalid_node_names(self) -> List[str]:
        invalid_nodes = []
        for node in self.name2node.values():
            for precondition in node.precondition:
                if not self.name2node[precondition].is_activated:
                    invalid_nodes.append(node)
                    break
        return [node.name for node in invalid_nodes]
    
    def __repr__(self) -> str:
        return f"PDLGraph({self.name2node})"
