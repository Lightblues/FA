from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn, json
app = FastAPI()

def get_api_model_by_endpoint(endpoint: str) -> str:
    """ Given the endpoint, return a readable API definition.
    """
    for route in app.routes:
        if route.path == endpoint and hasattr(route, 'response_model'):
            request_model = None
            # 获取请求模型
            if hasattr(route.endpoint, "__annotations__"):
                for param, param_type in route.endpoint.__annotations__.items():
                    if issubclass(param_type, BaseModel):
                        request_model = param_type
                        break
            response_model = route.response_model

            # 生成可读的API定义
            api_definition = f"## API Endpoint: {endpoint}\n\n"
            if request_model:
                # response_model.schema_json(indent=2)
                api_definition += "### Request Model:\n"
                api_definition += f"```json\n{json.dumps(request_model.model_json_schema(), indent=2)}\n```\n\n"
            if response_model:
                api_definition += "### Response Model:\n"
                api_definition += f"```json\n{json.dumps(response_model.model_json_schema(), indent=2)}\n```\n\n"

            return api_definition
    return "No models found for the given endpoint."

