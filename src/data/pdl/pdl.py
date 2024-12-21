from typing import Any, Dict, List

import yaml
from pydantic import BaseModel, Field
from typing import Union
from common import json_line

from .pdl_nodes import AnswerNode, BaseNode, ParameterNode, ToolDependencyNode
from .tool import FunctionDefinition, ToolDefinition


# def base_node_representer(dumper, data):
#     node_dict = {k: getattr(data, k) for k in data._print_keys if getattr(data, k)}
#     return dumper.represent_mapping('tag:yaml.org,2002:map', node_dict)
# # Register the custom representer for BaseNode
# yaml.add_representer(BaseNode, base_node_representer)


class MyDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def represent_scalar(self, tag, value, style=None):
        if style is None:
            if "\n" in value:
                style = "|"
        return super(MyDumper, self).represent_scalar(tag, value, style)


class PDL(BaseModel):
    Name: str
    Desc: str
    # Desc_detail: str
    APIs: List[ToolDependencyNode]
    SLOTs: List[ParameterNode]
    ANSWERs: List[AnswerNode]
    Procedure: str

    apis: List[ToolDefinition] = Field(default_factory=list)

    @classmethod
    def load_from_str(cls, PDL_str: str):
        ob = yaml.load(PDL_str, Loader=yaml.FullLoader)
        return cls(
            Name=ob["Name"],
            Desc=ob["Desc"],
            APIs=ob["APIs"],
            SLOTs=ob["SLOTs"],
            ANSWERs=ob["ANSWERs"],
            Procedure=ob["Procedure"],
        )

    @classmethod
    def load_from_file(cls, file_path):
        with open(file_path, "r") as f:
            PDL_str = f.read().strip()
        return cls.load_from_str(PDL_str)

    def add_tool(self, tool: Union[ToolDefinition, dict], precondition: List[str] = []):
        if isinstance(tool, dict):
            tool = ToolDefinition(**tool)
        self.apis.append(tool)
        self.APIs.append(ToolDependencyNode(tool, precondition))

    def __str__(self):
        _indented_procedure = "\n".join([f"    {line}" for line in self.Procedure.split("\n")])
        s = f"Name: {self.Name}\nDesc: {json_line(self.Desc)}\n"
        s += "SLOTs:\n"
        s += "\n".join([str(s) for s in self.SLOTs])
        s += "\nAPIs:\n"
        s += "\n".join([str(a) for a in self.APIs])
        s += "\nANSWERs:\n"
        s += "\n".join([str(a) for a in self.ANSWERs])
        s += f"\nProcedure: |-\n{_indented_procedure}"
        return s.strip()

    def to_str(self):
        selected_keys = ["Name", "Desc", "SLOTs", "APIs", "ANSWERs", "Procedure"]
        return self._format_with_yaml(selected_keys)

    def to_json(self):
        selected_keys = ["Name", "Desc", "SLOTs", "APIs", "ANSWERs", "Procedure"]
        return self.model_dump(include=selected_keys)

    def _format_with_yaml(self, selected_keys: List[str]) -> str:
        infos = self.model_dump()
        infos_selected = {k: infos[k] for k in selected_keys}
        s = yaml.dump(
            infos_selected,
            sort_keys=False,
            Dumper=MyDumper,
            default_flow_style=False,
            allow_unicode=True,
        )
        return s.strip()
