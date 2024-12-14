from typing import *
from enum import Enum
from pydantic import BaseModel

from ..common import *
from .node_data.base import NodeDataBase

# ---------------------------------------------------
# NodeData
# ---------------------------------------------------
class NodeTypeRegistry:
    _node_types: Dict[str, Type[NodeDataBase]] = {}
    
    @classmethod
    def register(cls, node_type: str, data_model: Type[NodeDataBase]):
        cls._node_types[node_type] = data_model
    
    @classmethod
    def get_data_model(cls, node_type: str) -> Type[NodeDataBase]:
        return cls._node_types.get(node_type)

# ---------------------------------------------------
# Inputs & Outputs
# ---------------------------------------------------
class _InputType(Enum):
    REFERENCE_OUTPUT = "REFERENCE_OUTPUT"
    REFERENCE_INPUT = "REFERENCE_INPUT"
    REFERENCE_PARAMETER = "REFERENCE_PARAMETER"

class _InputData(BaseModel):
    InputType: str
    Reference: Dict[str, Any]  # TODO: reference node representation

    def __str__(self):
        return f"{self.InputType} {self.Reference}"

class NodeInput(BaseModel):
    Name: str
    Type: str           # STRING
    Input: _InputData
    Desc: str

    def __str__(self):
        return f"[{self.Name}] ({self.Type}) {self.Input}"

# ---------------------------------------------------
# WorkflowNode
# ---------------------------------------------------
class WorkflowNodeBase(BaseModel):
    """Workflow node"""
    NodeID: str
    NodeName: str
    NodeDesc: str
    NodeType: str
    Inputs: List[NodeInput]
    Outputs: List[Dict[str, Any]]
    NextNodeIDs: List[str]
    NodeUI: str
    NodeData: NodeDataBase = None   # specific data model

    def __init__(self, **data):
        super().__init__(**data)
        # get different data model by node type! 
        if self.NodeType in NODE_TYPE_KEY_MAP:
            key = NODE_TYPE_KEY_MAP[self.NodeType]
            if key in data:
                data_model = NodeTypeRegistry.get_data_model(self.NodeType)
                if data_model:
                    self.NodeData = data_model(**data[key])
        else:
            self.NodeData = None

    def __str__(self):
        s = f"--- NODE {self.NodeName} ({self.NodeType}) ({self.NodeID}) ---\n"
        s += f"  Inputs: {' | '.join(str(x) for x in self.Inputs)}\n"
        s += f"  Outputs: {self.Outputs}\n"
        s += f"  NodeData: {self.NodeData}\n"
        return s
