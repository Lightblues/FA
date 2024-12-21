from typing import List, Optional

from pydantic import BaseModel, Field

from data.pdl.pdl_nodes import AnswerNode, BaseNode, ToolDependencyNode
from data.pdl.tool import ExtToolSpec, ToolParameter

from .base import Input, NodeType, TypeEnum
from .workflow_node_data import APIInfo, NodeDataBase, NodeType_Data_Map, NodeType_Key_Map
from .workflow_node_data import ToolNodeData


class InputParam(BaseModel):
    """输入参数"""

    Name: str
    Type: TypeEnum
    Input: Input
    Desc: Optional[str] = None

    def __str__(self):
        return f"(Name={self.Name}, Type={self.Type}, Input={self.Input}, Desc={self.Desc})"


class OutputParam(BaseModel):
    """输出参数"""

    Title: str
    Type: TypeEnum
    Required: List[str] = Field(default_factory=list)
    Properties: List["OutputParam"] = Field(default_factory=list)
    Desc: Optional[str] = None
    Value: Optional[Input] = None

    def __str__(self):
        properties = []
        for p in self.Properties:
            properties.append(f"(Name={self.Title}.{p.Title}, Type={p.Type}, Desc={p.Desc})")
        return f"[{', '.join(properties)}]"


class WorkflowNode(BaseModel):
    """工作流节点"""

    NodeID: str
    NodeName: str
    NodeDesc: str
    NodeType: NodeType
    Inputs: List[InputParam] = Field(default_factory=list)
    Outputs: List[OutputParam] = Field(default_factory=list)
    NextNodeIDs: List[str] = Field(default_factory=list)
    NodeUI: str
    NodeData: NodeDataBase = Field(default_factory=NodeDataBase)  # NOTE: will be rebuild in __init__

    def __init__(self, **data):
        super().__init__(**data)
        assert self.NodeType in NodeType_Data_Map, f"Invalid NodeType: {self.NodeType}"
        self.NodeData = NodeType_Data_Map[self.NodeType](**data[NodeType_Key_Map[self.NodeType]])

    def __str__(self):
        input_str = f"[{', '.join(str(i) for i in self.Inputs)}]"
        output_str = f"[{', '.join(str(i) for i in self.Outputs)}]"
        s = f"- NodeID: {self.NodeID}\n"
        s += f"  NodeName: {self.NodeName}\n"
        s += f"  NodeDesc: {self.NodeDesc}\n"
        s += f"  NodeType: {self.NodeType}\n"
        s += f"  Inputs: {input_str}\n"
        s += f"  Outputs: {output_str}\n"
        s += f"  NodeData: {self.NodeData}"
        return s

    def to_pdl(self):
        if self.NodeType in (NodeType.START, NodeType.PARAMETER_EXTRACTOR, NodeType.LOGIC_EVALUATOR):
            return self._default_node_to_pdl()
        elif self.NodeType == NodeType.ANSWER:
            return self._answer_to_pdl()
        elif self.NodeType == NodeType.TOOL:
            return self._tool_to_pdl()
        else:
            raise ValueError(f"Unsupported node type: {self.NodeType}")

    def _default_node_to_pdl(self) -> BaseNode:
        return BaseNode(
            name=self.NodeName,
            desc=self.NodeDesc,
            _type=self.NodeType,
            node_data=self.NodeData,
        )

    def _answer_to_pdl(self) -> AnswerNode:
        return AnswerNode(name=self.NodeName, desc=self.NodeData.Answer or self.NodeDesc)

    def _tool_to_pdl(self) -> ToolDependencyNode:
        return ToolDependencyNode(
            name=self.NodeName,
            desc=self.NodeDesc,
        )

    def to_tool_spec(self) -> ExtToolSpec:
        node_data: ToolNodeData = self.NodeData
        return ExtToolSpec(
            name=self.NodeName,
            description=self.NodeDesc,
            parameters=node_data.to_tool_spec(),
            url=node_data.API.URL,
            method=node_data.API.Method,
        )
