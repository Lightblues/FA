from typing import Any, Dict, List

from pydantic import BaseModel

from common import json_line


class ParameterNode(BaseModel):
    name: str
    desc: str
    type: str

    def __str__(self):
        return f"- name: {self.name}\n  desc: {json_line(self.desc)}\n  type: {self.type}"


class BaseNode(BaseModel):
    type: str = "default"
    name: str
    desc: str
    # node_data: Any = None   # NOTE: for compatibility with Huabu NodeData


class AnswerNode(BaseNode):
    type: str = "answer"
    answer: str

    def __str__(self):
        return f"- name: {self.name}\n  answer: {json_line(self.answer)}"


class ToolParam(BaseModel):
    ParamName: str
    ParamDesc: str
    ParamType: str
    IsRequired: bool


class ToolNode(BaseNode):
    type: str = "tool"
    URL: str
    Method: str
    Query: List[ToolParam]
    Body: List[ToolParam]

    def __str__(self):
        s_query = [f"(name={p.ParamName}, type={p.ParamType}, required={p.IsRequired})" for p in self.Query]
        s_body = [f"(name={p.ParamName}, type={p.ParamType}, required={p.IsRequired})" for p in self.Body]
        return f"- name: {self.name}\n  desc: {self.desc}\n  API: {self.URL}\n  Query: [{', '.join(s_query)}]\n  Body: [{', '.join(s_body)}]"


class PDL(BaseModel):
    Name: str
    Desc: str
    # Desc_detail: str
    APIs: List[ToolNode]
    SLOTs: List[ParameterNode]
    ANSWERs: List[AnswerNode]
    Procedure: str

    def __str__(self):
        s = f"Name: {self.Name}\nDesc: {json_line(self.Desc)}\n"
        s += "SLOTs:\n"
        s += "\n".join([str(s) for s in self.SLOTs])
        s += "\nAPIs:\n"
        s += "\n".join([str(a) for a in self.APIs])
        s += "\nANSWERs:\n"
        s += "\n".join([str(a) for a in self.ANSWERs])
        s += f"\nProcedure: {json_line(self.Procedure)}"
        return s
