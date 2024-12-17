from pydantic import BaseModel
from typing import *
from enum import Enum
from .base import NodeDataBase

class _Reference(BaseModel):
    NodeID: str
    JsonPath: str

class _UserInput(BaseModel):
    UserInputValue: List[str]

class _InputTypeEnum(Enum):
    REFERENCE_OUTPUT = "REFERENCE_OUTPUT"       # Reference -> _Reference
    USER_INPUT = "USER_INPUT"                   # Fixed value -> _UserInput

class _LogicOperatorEnum(Enum):
    UNSPECIFIED = "UNSPECIFIED"
    EQ = "EQ"
    NE = "NE"
    GT = "GT"
    LT = "LT"
    GE = "GE"
    LE = "LE"

    def __str__(self):
        return self.value

class _LogicLeftRight(BaseModel):
    """ 
    {
        "InputType": "USER_INPUT",
        "UserInputValue": {
            "Values": ["白金卡"]
        }
    },
    {
        "InputType": "REFERENCE_OUTPUT",
        "Reference": {
            "NodeID": "0fa5e5a6-95fb-016e-8d08-50901034a8ea",
            "JsonPath": "Output.invoicing_progress"
        }
    }
    """
    InputType: _InputTypeEnum
    Reference: _Reference = None
    UserInput: Union[_UserInput, None] = None # NOTE that UserInput can be None whetn InputType="USER_INPUT" (default branch)

    def __str__(self):
        if self.InputType == _InputTypeEnum.REFERENCE_OUTPUT:
            return f"Reference({self.Reference.NodeID}.{self.Reference.JsonPath})"
        elif self.InputType == _InputTypeEnum.USER_INPUT:
            return 'Default' if self.UserInput is None else  f"UserInput({self.UserInput.UserInputValue})"
        else:
            raise ValueError(f"Invalid input type: {self.InputType}")


class _LogicComparison(BaseModel):
    Left: _LogicLeftRight
    LeftType: str
    Operator: _LogicOperatorEnum
    Right: _LogicLeftRight
    MatchType: str  # TODO: to enum | SEMANTIC

    def __str__(self):
        return f"{self.Left} {self.Operator} {self.Right}"

class _LogicLogical(BaseModel):
    LogicalOperator: _LogicOperatorEnum
    Compound: List[Any] = []     # OR | AND TODO: what does it mean?
    Comparison: _LogicComparison = None

    def __str__(self):
        return f"(LogicalOperator={self.LogicalOperator}, Compound={self.Compound}, Comparison={self.Comparison})"

class _LogicCondition(BaseModel):
    NextNodeIDs: List[str]
    Logical: _LogicLogical = None  # NOTE for the default condition, cannot None!

    def __str__(self):
        return f"{self.Logical} -> {self.NextNodeIDs}"


class LogicEvaluatorNodeData(NodeDataBase):
    Group: List[_LogicCondition]

    def __str__(self):
        return "[LOGIC] " + " | ".join(f"({c})" for c in self.Group)
