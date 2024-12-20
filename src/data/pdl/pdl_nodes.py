from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from common import json_line


class BaseNode(BaseModel):
    _type: str = "default"
    _print_keys = ["name", "desc"]

    name: str
    desc: str = ""

    def __str__(self):
        s = f"- name: {self.name}"
        for k in self._print_keys:
            if getattr(self, k):
                v = getattr(self, k)
                if not v:
                    continue
                s += f"\n  {k}: {json_line(v)}"
        return s


class ParameterNode(BaseNode):
    _type: str = "parameter"
    _print_keys = ["name", "desc", "type"]

    type: str = ""  # TODO: Literal


class AnswerNode(BaseNode):
    _type: str = "answer"
    _print_keys = ["name", "desc"]


class ToolDependencyNode(BaseNode):
    _type: str = "tool_dependency"
    _print_keys = ["name", "desc", "precondition"]
    precondition: List[str] = Field(default_factory=list)
