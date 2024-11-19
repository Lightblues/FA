# api_registry.py
import json
from typing import Dict, Type
from pydantic import BaseModel
from dataclasses import dataclass, asdict, field


@dataclass
class APIInfo:
    name: str
    description: str
    request_model: Type[BaseModel]
    response_model: Type[BaseModel]
    
    def to_readable_markdown_api_definition(self) -> str:
        _request_str = json.dumps(self.request_model.model_json_schema(), indent=2) if self.request_model else ""
        _response_str = json.dumps(self.response_model.model_json_schema(), indent=2) if self.response_model else ""
        api_definition = f"## {self.name}\n\n"
        api_definition += f"{self.description}\n\n"
        api_definition += "### Request Model:\n"
        api_definition += f"```json\n{_request_str}\n```\n\n"
        api_definition += "### Response Model:\n"
        api_definition += f"```json\n{_response_str}\n```\n\n"
        return api_definition

class APIRegistry:
    def __init__(self):
        self.registry: Dict[str, APIInfo] = {}

    def register_api(self, name: str, description: str, request_model: Type[BaseModel], response_model: Type[BaseModel]):
        self.registry[name] = APIInfo(name, description, request_model, response_model)

    def get_api_info(self, name: str) -> APIInfo:
        return self.registry.get(name, None)

api_registry = APIRegistry()


def register_api(name: str, description: str, request_model: Type[BaseModel], response_model: Type[BaseModel]):
    api_registry.register_api(name, description, request_model, response_model)
    # 增加中文接口? -- check 一下API prompt!
    # api_registry.register_api(description, name, request_model, response_model)