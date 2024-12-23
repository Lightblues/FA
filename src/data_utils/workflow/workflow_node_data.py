"""Node data type definitions based on workflow.proto"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from common import json_line
from data.pdl.tool import ToolParameter, ToolProperties
from .base import Input, NodeType, TypeEnum


# --- Base Node Data ---
class NodeDataBase(BaseModel):
    """节点数据基类"""

    def __str__(self):
        # return f"{self.__class__.__name__}"
        return ""


# --- Tool Node Data ---
class RequestParam(BaseModel):
    ParamName: str
    ParamDesc: str
    ParamType: TypeEnum
    Input: Input
    IsRequired: bool = False
    SubParams: List["RequestParam"] = Field(default_factory=list)

    def __str__(self):
        return f"Param(Name={self.ParamName}, Type={self.ParamType}, Input={self.Input})"


class APIInfo(BaseModel):
    URL: str
    Method: str
    authType: str = "NONE"
    KeyLocation: str = "HEADER"
    KeyParamName: str = ""
    KeyParamValue: str = ""

    def __str__(self):
        return f"API(Method={self.Method}, URL={self.URL})"


class ToolNodeData(NodeDataBase):
    """工具节点数据"""

    API: APIInfo
    Header: List[Dict] = Field(default_factory=list)
    Query: List[RequestParam] = Field(default_factory=list)
    Body: List[RequestParam] = Field(default_factory=list)

    def __str__(self):
        query_str = "[" + ", ".join(f"{q}" for q in self.Query) + "]"
        body_str = "[" + ", ".join(f"{b}" for b in self.Body) + "]"
        return f"API={self.API}, Query={query_str}, Body={body_str}"

    def to_tool_spec(self) -> ToolProperties:
        # Transform Query/Body to ToolProperties
        properties = {}
        required = []
        for param in self.Query + self.Body:
            properties[param.ParamName] = ToolParameter(
                type=param.ParamType.value.lower(),  # NOTE be careful about the case
                description=param.ParamDesc,
                # FIXME: enum
            )
            if param.IsRequired:
                required.append(param.ParamName)
        return ToolProperties(properties=properties, required=required)


# --- Answer Node Data ---
class AnswerNodeData(NodeDataBase):
    """回复节点数据"""

    Answer: str

    def __str__(self):
        return f"Answer={json_line(self.Answer)[:50]}..."


# --- LLM Node Data ---
class LLMNodeData(NodeDataBase):
    """大模型节点数据"""

    ModelName: str
    Temperature: float
    TopP: float
    MaxTokens: int
    Prompt: str

    def __str__(self):
        return f"ModelName={self.ModelName}, Prompt={json_line(self.Prompt)[:50]}..."


# --- Parameter Extractor Node Data ---
class ParameterExtractorNodeData(NodeDataBase):
    """参数提取节点数据"""

    class Parameter(BaseModel):
        RefParameterID: str
        Required: bool = False

        def __str__(self):
            return f"(RefParameterID={self.RefParameterID}, Required={self.Required})"

    Parameters: List[Parameter] = Field(default_factory=list)
    UserConstraint: str = ""

    def __str__(self):
        return f"Parameters=[{', '.join(str(p) for p in self.Parameters)}], UserConstraint={json_line(self.UserConstraint)[:50]}..."


# --- Logic Evaluator Node Data ---
class ComparisonExpression(BaseModel):
    """比较表达式"""

    class LogicMatchTypeEnum(Enum):
        """匹配类型"""

        SEMANTIC = "SEMANTIC"  # 语义匹配
        PRECISE = "PRECISE"  # 精确匹配

        def __str__(self):
            return f"{self.value}"

    class ComparisonOperatorEnum(Enum):
        """比较算符"""

        UNSPECIFIED = "UNSPECIFIED"
        EQ = "EQ"  # Equal
        NE = "NE"  # Not Equal
        LT = "LT"  # Less Than
        LE = "LE"  # Less Than or Equal
        GT = "GT"  # Greater Than
        GE = "GE"  # Greater Than or Equal
        IS_SET = "IS_SET"  # Has Value
        NOT_SET = "NOT_SET"  # No Value
        CONTAINS = "CONTAINS"  # Contains
        NOT_CONTAINS = "NOT_CONTAINS"  # Not Contains
        IN = "IN"  # In
        NOT_IN = "NOT_IN"  # Not In

        def __str__(self):
            return f"{self.value}"

    Left: Input
    LeftType: str
    Operator: ComparisonOperatorEnum
    Right: Input
    MatchType: LogicMatchTypeEnum = LogicMatchTypeEnum.PRECISE

    def __str__(self):
        return f"Comparison(Left={self.Left}, Operator={self.Operator}, Right={self.Right})"


class LogicOperatorEnum(Enum):
    """逻辑运算符"""

    UNSPECIFIED = "UNSPECIFIED"  # Comparison
    AND = "AND"  # Compound
    OR = "OR"

    def __str__(self):
        return f"{self.value}"


class LogicalExpression(BaseModel):
    """逻辑表达式"""

    LogicalOperator: LogicOperatorEnum
    Compound: List["LogicalExpression"] = Field(default_factory=list)
    Comparison: Optional[ComparisonExpression] = None

    def __str__(self):
        if self.LogicalOperator == LogicOperatorEnum.UNSPECIFIED:
            return f"{self.Comparison}"
        else:
            return f"LogicalExpression(LogicalOperator={self.LogicalOperator}, Compound=[{', '.join(str(c) for c in self.Compound)}])"


class LogicalGroup(BaseModel):
    """逻辑组"""

    NextNodeIDs: List[str] = Field(default_factory=list)
    Logical: Optional[LogicalExpression] = None

    def __str__(self):
        return f"Group(Logical={self.Logical}, NextNodeIDs={self.NextNodeIDs})"


class LogicEvaluatorNodeData(NodeDataBase):
    """逻辑判断节点数据"""

    Group: List[LogicalGroup] = Field(default_factory=list)

    def __str__(self):
        return f"[{', '.join(str(g) for g in self.Group)}]"


# --- Code Executor Node Data ---
class CodeExecutorNodeData(NodeDataBase):
    """代码行节点数据"""

    class LanguageType(Enum):
        PYTHON3 = "PYTHON3"

    Code: str
    Language: LanguageType = LanguageType.PYTHON3

    def __str__(self):
        return f"Code={json_line(self.Code)[:50]}..."


# --- Start Node Data ---
class StartNodeData(NodeDataBase):
    """开始节点数据"""


# --- End Node Data ---
class EndNodeData(NodeDataBase):
    """结束节点数据"""


# Handle recursive references
RequestParam.model_rebuild()
LogicalExpression.model_rebuild()


NodeType_Data_Map = {
    NodeType.TOOL: ToolNodeData,
    NodeType.ANSWER: AnswerNodeData,
    NodeType.LLM: LLMNodeData,
    NodeType.PARAMETER_EXTRACTOR: ParameterExtractorNodeData,
    NodeType.LOGIC_EVALUATOR: LogicEvaluatorNodeData,
    NodeType.CODE_EXECUTOR: CodeExecutorNodeData,
    NodeType.START: StartNodeData,
    NodeType.END: EndNodeData,
}
NodeType_Key_Map = {
    NodeType.TOOL: "ToolNodeData",
    NodeType.ANSWER: "AnswerNodeData",
    NodeType.LLM: "LLMNodeData",
    NodeType.PARAMETER_EXTRACTOR: "ParameterExtractorNodeData",
    NodeType.LOGIC_EVALUATOR: "LogicEvaluatorNodeData",
    NodeType.CODE_EXECUTOR: "CodeExecutorNodeData",
    NodeType.START: "StartNodeData",
    NodeType.END: "EndNodeData",
}
