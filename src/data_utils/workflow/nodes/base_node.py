""" 
@241209
- [x] implement WorkflowNodeBase
@241216
- [x] implement to_pdl() for node: ANSWER, TOOL
"""
from typing import *
from pydantic import BaseModel

from ..common import *
from .node_data.base import NodeDataBase
from .node_data.tool_node_data import _TOOL_QUERY
from pdl.typings import *
from .node_input import NodeOutput
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
# WorkflowNode
# ---------------------------------------------------
class WorkflowNodeBase(BaseModel):
    """Workflow node"""
    NodeID: str
    NodeName: str
    NodeDesc: str
    NodeType: str
    Inputs: List[Any]           # ...
    Outputs: List[NodeOutput]
    NextNodeIDs: List[str]
    # NodeUI: Union[_NodeUI, str]
    NodeUI: str                     # NOTE do not need NodeUI for now
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
        # # load the UI data
        # if isinstance(self.NodeUI, str):
        #     self.NodeUI = _NodeUI(**json.loads(self.NodeUI))

    def __str__(self):
        s = f"- NODE: {self.NodeName} ({self.NodeType}) ({self.NodeID})\n"
        s += f"  Inputs: {' | '.join(str(x) for x in self.Inputs)}\n"
        s += f"  Outputs: {self.Outputs}\n"
        s += f"  NodeData: {self.NodeData}"
        return s

    def to_pdl(self):
        if self.NodeType in ("START", "PARAMETER_EXTRACTOR", "LOGIC_EVALUATOR"): return self._default_node_to_pdl()
        elif self.NodeType == "ANSWER": return self._answer_to_pdl()
        elif self.NodeType == "TOOL": return self._tool_to_pdl()
        else: raise ValueError(f"Unsupported node type: {self.NodeType}")
    
    def _default_node_to_pdl(self) -> BaseNode:
        return BaseNode(
            name=self.NodeName,
            desc=self.NodeDesc,
            type=self.NodeType,
            node_data=self.NodeData
        )

    def _answer_to_pdl(self) -> AnswerNode:
        return AnswerNode(
            name=self.NodeName,
            desc=self.NodeDesc,
            answer=self.NodeData.Answer
        )

    def _tool_to_pdl(self) -> ToolNode:
        def _convert_param(param: _TOOL_QUERY) -> ToolParam:
            return ToolParam(
                ParamName=param.ParamName,
                ParamDesc=param.ParamDesc,
                ParamType=param.ParamType,
                IsRequired=param.IsRequired,
                Input=param.Input
            )

        return ToolNode(
            name=self.NodeName,
            desc=self.NodeDesc,
            API=self.NodeData.API,
            Header=self.NodeData.Header,
            Query=[_convert_param(param) for param in self.NodeData.Query],
            Body=[_convert_param(param) for param in self.NodeData.Body]
        )
