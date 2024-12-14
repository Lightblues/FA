from pydantic import BaseModel
from typing import *
from .base import NodeDataBase

class _LogicComparison(BaseModel):
    Left: Any
    LeftType: str
    Operator: str  # TODO: to enum. 
    Right: Any     # TODO: to enum | USER_INPUT (固定值) | REFERENCE_OUTPUT
    MatchType: str  # TODO: to enum | SEMANTIC

class _LogicLogical(BaseModel):
    LogicalOperator: str  # TODO: to enum
    Compound: List[Any]     # OR | 
    Comparison: _LogicComparison = None

class _LogicCondition(BaseModel):
    NextNodeIDs: List[str]
    Logical: _LogicLogical = None  # NOTE for the default condition, cannot None!
    # TODO: __str__ (if ..., then )
    #   use NodeID -> NodeName map

class LogicEvaluatorNodeData(NodeDataBase):
    Group: List[_LogicCondition]

    def __str__(self):
        return "[LOGIC] " + " | ".join(str(c) for c in self.Group)
