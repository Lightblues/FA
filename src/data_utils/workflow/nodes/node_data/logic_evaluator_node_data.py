from enum import Enum
from typing import *

from pydantic import BaseModel

from ...variable import Variable
from .base import NodeDataBase


class _LogicalOperatorEnum(Enum):
    UNSPECIFIED = "UNSPECIFIED"  # Comparison
    AND = "AND"  # Compound
    OR = "OR"

    def __str__(self):
        return self.value


class _LogicOperatorEnum(Enum):
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
        return self.value


class _LogicMatchTypeEnum(Enum):
    SEMANTIC = "SEMANTIC"
    PRECISE = "PRECISE"

    def __str__(self):
        return self.value


class _ComparisonExpression(BaseModel):
    Left: Variable
    LeftType: str
    Operator: _LogicOperatorEnum
    Right: Variable
    MatchType: _LogicMatchTypeEnum

    def __str__(self):
        return f"{self.Left} {self.Operator} {self.Right}"


class _LogicalExpression(BaseModel):
    LogicalOperator: _LogicalOperatorEnum
    Compound: List["_LogicalExpression"] = []
    Comparison: _ComparisonExpression = None

    def __str__(self):
        return f"(LogicalOperator={self.LogicalOperator}, Compound={self.Compound}, Comparison={self.Comparison})"


class _LogicalGroup(BaseModel):
    NextNodeIDs: List[str]
    Logical: _LogicalExpression = None  # NOTE for the default condition, cannot None!

    def __str__(self):
        return f"{self.Logical} -> {self.NextNodeIDs}"


class LogicEvaluatorNodeData(NodeDataBase):
    Group: List[_LogicalGroup]

    def __str__(self):
        return "[LOGIC] " + " | ".join(f"({c})" for c in self.Group)
