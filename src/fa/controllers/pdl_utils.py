"""Graph structure of PDL & Graph-based Dependency Controller
updated @240918

"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from data import PDL


class PDLNode(BaseModel):
    name: str
    precondition: Optional[List[str]] = Field(default_factory=list)
    is_activated: bool = False

    def __repr__(self) -> str:
        return f"PDLNode({self.name}, with precondition {self.precondition})"


class PDLGraph(BaseModel):
    name2node: Optional[Dict[str, PDLNode]] = Field(default_factory=dict)

    def add_node(self, node: PDLNode):
        assert node.name not in self.name2node, f"node {node.name} already exists!"
        self.name2node[node.name] = node

    def check_preconditions(self) -> bool:
        names = set(self.name2node.keys())
        for node in self.name2node.values():
            for name in node.precondition:
                if not name:
                    continue
                assert name in names, f"precondition `{name}` not found in nodes: {names}!!"
        return True

    def get_invalid_node_names(self) -> set[str]:
        """Get the names list of invalid nodes"""
        invalid_nodes = []
        for node in self.name2node.values():
            for precondition in node.precondition:
                if not self.name2node[precondition].is_activated:
                    invalid_nodes.append(node)
                    break
        return {node.name for node in invalid_nodes}

    def __repr__(self) -> str:
        return f"PDLGraph({self.name2node})"

    @classmethod
    def from_pdl(cls, pdl: PDL):
        """Build PDL Graph from PDL"""
        if (pdl.APIs is None) or (not pdl.APIs):  # if pdl.apis is None
            pdl.APIs = []
        g = PDLGraph()
        for api in pdl.APIs:
            node = PDLNode(name=api.name, precondition=api.precondition or [])
            g.add_node(node)
        g.check_preconditions()
        return g
