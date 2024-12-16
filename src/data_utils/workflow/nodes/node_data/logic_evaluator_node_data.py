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
    UserInput: _UserInput = None

class _LogicComparison(BaseModel):
    Left: _LogicLeftRight
    LeftType: str
    Operator: _LogicOperatorEnum
    Right: _LogicLeftRight
    MatchType: str  # TODO: to enum | SEMANTIC

class _LogicLogical(BaseModel):
    LogicalOperator: _LogicOperatorEnum
    Compound: List[Any]     # OR | AND
    Comparison: _LogicComparison = None

class _LogicCondition(BaseModel):
    NextNodeIDs: List[str]
    Logical: _LogicLogical = None  # NOTE for the default condition, cannot None!
    # TODO __str__ (if ..., then )
    #   use NodeID -> NodeName map

class LogicEvaluatorNodeData(NodeDataBase):
    Group: List[_LogicCondition]

    def __str__(self):
        return "[LOGIC] " + " | ".join(str(c) for c in self.Group)
