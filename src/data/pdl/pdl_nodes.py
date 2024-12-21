from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from common import json_line
from data.pdl.tool import ToolParameterType


class BaseNode(BaseModel):
    _type: str = "default"
    _print_keys = ["name", "desc"]

    name: str = None
    desc: Optional[str] = None

    def __str__(self):
        s = f"- name: {self.name}"
        _print_keys = [k for k in self._print_keys if k != "name"]
        for k in _print_keys:
            if getattr(self, k):
                v = getattr(self, k)
                if not v:
                    continue
                s += f"\n  {k}: {json_line(v)}"
        return s


class ParameterNode(BaseNode):
    _type: str = "parameter"
    _print_keys = ["name", "desc", "type"]

    type: Optional[ToolParameterType] = None


class AnswerNode(BaseNode):
    _type: str = "answer"
    _print_keys = ["name", "desc"]


class ToolDependencyNode(BaseNode):
    _type: str = "tool_dependency"
    _print_keys = ["name", "precondition"]
    precondition: Optional[List[str]] = None
