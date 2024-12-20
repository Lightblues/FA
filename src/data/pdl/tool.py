from typing import List

from pydantic import BaseModel


class ToolParam(BaseModel):
    ParamName: str
    ParamDesc: str
    ParamType: str
    IsRequired: bool


class ToolNode(BaseModel):
    _type: str = "tool"
    URL: str
    Method: str
    Query: List[ToolParam]
    Body: List[ToolParam]

    def __str__(self):
        s_query = [f"(name={p.ParamName}, type={p.ParamType}, required={p.IsRequired})" for p in self.Query]
        s_body = [f"(name={p.ParamName}, type={p.ParamType}, required={p.IsRequired})" for p in self.Body]
        return f"- name: {self.name}\n  desc: {self.desc}\n  API: {self.URL}\n  Query: [{', '.join(s_query)}]\n  Body: [{', '.join(s_body)}]"
