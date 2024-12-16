from pydantic import BaseModel
from typing import List, Dict, Any
from data_utils.workflow.nodes.node_data.tool_node_data import _TOOL_API

class BaseNode(BaseModel):
    type: str = "default"
    name: str
    desc: str
    node_data: Any = None # NOTE: for compatibility with Huabu NodeData


class AnswerNode(BaseNode):
    type: str = "answer"
    answer: str


class ToolParam(BaseModel):
    ParamName: str
    ParamDesc: str
    ParamType: str
    # Input: _TOOL_INPUT  # NOTE: compared to online Huabu , remove the input field
    IsRequired: bool
    # SubParams: List[Dict[str, Any]]

class ToolNode(BaseNode):
    type: str = "tool"
    API: _TOOL_API
    Header: List[Dict[str, Any]]
    Query: List[ToolParam]
    Body: List[ToolParam]


class PDL(BaseModel):
    Name: str
    Desc: str
    # Desc_detail: str
    APIs: List[ToolNode]
    SLOTs: List[str]
    ANSWERs: List[AnswerNode]
    Procedure: str
