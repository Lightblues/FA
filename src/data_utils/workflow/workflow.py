"""Workflow

NOTE:
1. edge: `source, target` is -> NodeID
"""

from typing import *

from pydantic import BaseModel

from .nodes import WorkflowNodeBase


class WorkflowEdge(BaseModel):
    """Workflow edge"""

    source: str
    sourceHandle: Optional[str] = None
    target: str
    type: str
    data: dict
    id: str
    selected: bool
    animated: bool

    def __str__(self) -> str:
        s = f"- Edge: '{self.source} -> {self.target}'"
        return s


class Workflow(BaseModel):
    """Workflow"""

    ProtoVersion: str
    WorkflowID: str
    WorkflowName: str
    WorkflowDesc: str
    Nodes: list[WorkflowNodeBase]
    Edges: list[WorkflowEdge]
    node_id_to_node: Dict[str, WorkflowNodeBase] = {}

    def __init__(self, **data):
        super().__init__(**data)
        # create node_id to node mapping
        self.node_id_to_node = {node.NodeID: node for node in self.Nodes}

    def __getitem__(self, node_id: str) -> WorkflowNodeBase:
        """Allow the workflow to be indexed by node_id"""
        return self.node_id_to_node[node_id]

    def __str__(self) -> str:
        s = f"Name: {self.WorkflowName}\nDesc: {self.WorkflowDesc}\n"
        s += "Nodes:\n"
        for node in self.Nodes:
            s += f"{node}\n"
        s += "Edges:\n"
        for edge in self.Edges:
            s += f"{edge}\n"
        return s

    def check_validation(self) -> bool:
        """Check the edge infos for PDL conversion
        NOTE: only used in EDA

        - [x] edges: check that the source and target are valid node ids
        - [ ] node.LogicEvaluator...Reference: check JsonPath
        """
        # 1. edges
        for edge in self.Edges:
            if (edge.source not in self.node_id_to_node) or (edge.target not in self.node_id_to_node):
                raise ValueError(f"Invalid edge: {edge}")
        return True
