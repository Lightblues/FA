from pydantic import BaseModel
from typing import *
from .common import NODE_TYPE_KEY_MAP
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

class Workflow(BaseModel):
    """Workflow"""
    ProtoVersion: str
    WorkflowID: str
    WorkflowName: str
    WorkflowDesc: str
    Nodes: list[WorkflowNodeBase]
    Edges: list[WorkflowEdge]

