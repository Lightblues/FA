"""Base type definitions for workflow"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class TypeEnum(Enum):
    """参数类型"""

    STRING = "STRING"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    OBJECT = "OBJECT"
    ARRAY_STRING = "ARRAY_STRING"
    ARRAY_INT = "ARRAY_INT"
    ARRAY_FLOAT = "ARRAY_FLOAT"
    ARRAY_BOOL = "ARRAY_BOOL"
    ARRAY_OBJECT = "ARRAY_OBJECT"

    def __str__(self):
        return self.value


class ReferenceFromNode(BaseModel):
    """引用其他节点的输出"""

    NodeID: str
    JsonPath: str

    def __str__(self):
        return f"{self.NodeID}.{self.JsonPath}"


class UserInputContent(BaseModel):
    """用户输入内容"""

    Values: List[str]


class SystemVariable(BaseModel):
    """系统变量"""

    Name: str
    DialogHistoryLimit: Optional[int] = None


class Input(BaseModel):
    """输入来源"""

    class InputSourceEnum(Enum):
        USER_INPUT = "USER_INPUT"  # 用户输入
        REFERENCE_OUTPUT = "REFERENCE_OUTPUT"  # 引用其他节点的输出
        SYSTEM_VARIABLE = "SYSTEM_VARIABLE"  # 系统变量
        CUSTOM_VARIABLE = "CUSTOM_VARIABLE"  # 自定义变量（API参数）
        NODE_INPUT_PARAM = "NODE_INPUT_PARAM"  # 当前节点内定义的输入变量的名称

        def __str__(self):
            return self.value

    InputType: InputSourceEnum
    UserInputValue: Optional[UserInputContent] = None
    Reference: Optional[ReferenceFromNode] = None
    SystemVariable: Optional["SystemVariable"] = None
    CustomVarID: Optional[str] = None
    NodeInputParamName: Optional[str] = None

    def __str__(self):
        if self.InputType == self.InputSourceEnum.USER_INPUT:
            return f"UserInputValue[{self.UserInputValue}]"
        elif self.InputType == self.InputSourceEnum.REFERENCE_OUTPUT:
            return f"Reference[{self.Reference}]"
        elif self.InputType == self.InputSourceEnum.SYSTEM_VARIABLE:
            return f"SystemVariable[{self.SystemVariable}]"
        elif self.InputType == self.InputSourceEnum.CUSTOM_VARIABLE:
            return f"CustomVarID[{self.CustomVarID}]"
        elif self.InputType == self.InputSourceEnum.NODE_INPUT_PARAM:
            return f"NodeInputParamName[{self.NodeInputParamName}]"
        else:
            raise ValueError(f"Invalid InputType: {self.InputType}")


class NodeType(Enum):
    """节点类型"""

    UNKNOWN = "UNKNOWN"
    START = "START"  # StartNodeData
    PARAMETER_EXTRACTOR = "PARAMETER_EXTRACTOR"  # ParameterExtractorNodeData
    LLM = "LLM"  # LLMNodeData
    LLM_KNOWLEDGE_QA = "LLM_KNOWLEDGE_QA"  # LLMKnowledgeQANodeData
    KNOWLEDGE_RETRIEVER = "KNOWLEDGE_RETRIEVER"  # KnowledgeRetrieverNodeData
    TAG_EXTRACTOR = "TAG_EXTRACTOR"  # TagExtractorNodeData
    CODE_EXECUTOR = "CODE_EXECUTOR"  # CodeExecutorNodeData
    TOOL = "TOOL"  # ToolNodeData
    LOGIC_EVALUATOR = "LOGIC_EVALUATOR"  # LogicEvaluatorNodeData
    ANSWER = "ANSWER"  # AnswerNodeData
    OPTION_CARD = "OPTION_CARD"  # OptionCardNodeData
    ITERATION = "ITERATION"  # IterationNodeData
    INTENT_RECOGNITION = "INTENT_RECOGNITION"  # IntentRecognitionNodeData
    WORKFLOW_REF = "WORKFLOW_REF"  # WorkflowRefNodeData
    PLUGIN = "PLUGIN"  # PluginNodeData
    END = "END"  # EndNodeData

    def __str__(self):
        return self.value


WORKFLOW_NODE_TYPES = [
    "CODE_EXECUTOR",
    "PARAMETER_EXTRACTOR",
    "LLM",
    "LLM_KNOWLEDGE_QA",
    "LOGIC_EVALUATOR",
    "ANSWER",
    "KNOWLEDGE_RETRIEVER",
    "START",
    "TOOL",
]
WORKFLOW_NODE_PROPERTIES = [
    "NodeID",
    "NodeName",
    "NodeDesc",
    "NodeType",
    "Inputs",
    "Outputs",
    "NextNodeIDs",
    "NodeUI",
]
NODE_TYPE_KEY_MAP = {
    "CODE_EXECUTOR": "CodeExecutorNodeData",  # ['Code', 'Language']
    "PARAMETER_EXTRACTOR": "ParameterExtractorNodeData",  # ['Parameters', 'UserConstraint']
    "LLM": "LLMNodeData",  # ['ModelName', 'Temperature', 'TopP', 'MaxTokens', 'Prompt']
    "LLM_KNOWLEDGE_QA": "LLMKnowledgeQANodeData",  # ['Query', 'ModelName', 'Filter', 'DocIDs', 'DocBizIDs', 'AllQA', 'Labels', 'DocRecallCount', 'DocConfidence', 'QARecallCount', 'QAConfidence']
    "LOGIC_EVALUATOR": "LogicEvaluatorNodeData",  # ['Group']
    "ANSWER": "AnswerNodeData",  # ['Answer']
    "KNOWLEDGE_RETRIEVER": "KnowledgeRetrieverNodeData",  # ['Query', 'Filter', 'DocIDs', 'DocBizIDs', 'AllQA', 'Labels', 'DocRecallCount', 'DocConfidence', 'QARecallCount', 'QAConfidence']
    "START": "StartNodeData",  # []
    "TOOL": "ToolNodeData",  # ['API', 'Header', 'Query', 'Body']
}
