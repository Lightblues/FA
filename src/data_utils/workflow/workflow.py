"""Workflow related type definitions based on workflow.proto"""

from enum import Enum
from typing import Annotated, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .base import Input, NodeType, TypeEnum
from .workflow_node import WorkflowNode


class WorkflowProtoVersion(Enum):
    """工作流的协议版本号"""

    UNSPECIFIED = "UNSPECIFIED"
    V2_6 = "V2_6"


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
    """工作流"""

    ProtoVersion: WorkflowProtoVersion
    WorkflowID: str
    WorkflowName: str
    WorkflowDesc: str
    Nodes: List[WorkflowNode]
    # Edge: str  # JSON string of edges
    Edges: List[WorkflowEdge]

    def __str__(self) -> str:
        s = f"Name: {self.WorkflowName}\nDesc: {self.WorkflowDesc}\n"
        s += "Nodes:\n"
        for node in self.Nodes:
            s += f"{node}\n"
        s += "Edges:\n"
        for edge in self.Edges:
            s += f"{edge}\n"
        return s
