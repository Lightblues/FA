import json
import pathlib
import sys

import jinja2


_DIR = pathlib.Path(__file__).parent
sys.path.append(str(_DIR.parent))
from dataclasses import dataclass, field
from typing import Dict

from common import LLM_CFG, Formater, OpenAIClient, init_client

from .api_registry import api_registry


@dataclass
class APICalling_Info:
    name: str = ""
    # args: List
    kwargs: Dict = field(default_factory=dict)


template = """## Task
You need to act as an API backend to process the request.

## API Definition
{{ API }}

## The request parameters
{{ api_params }}

## Your response
Please generate the API response based on the above information. NOTE:
1. Simulate the behavior of a real API server. You may generate some data if necessary.
    For boolean output, do not always return success!
2. If the input parameters are invalid, missing, meaningless, or do not meet the requirements, return detailed error information!
3. The response should always be in Chinese.
4. Output in JSON format."""


class Mocker:
    """
    Usage::

        mocker = Mocker(model_name="gpt-4o")
        register_api("query_news", "查询新闻", NewsQueryRequest, NewsQueryResponse)
        query = APICalling_Info(name="query_news", kwargs={"news_location": "上海", "news_type": "体育", "news_time": "2024-08-30"})
        res = mocker.mock_api_response(query)
    """

    client: OpenAIClient

    def __init__(self, model_name: str):
        self.client = init_client(llm_cfg=LLM_CFG[model_name])

    def mock_api_response(self, query: APICalling_Info):
        print(f"> calling {query.name} with {query.kwargs}")
        api_info = api_registry.get_api_info(query.name)
        api_definition = api_info.to_readable_markdown_api_definition()
        prompt = jinja2.Template(template).render(API=api_definition, api_params=query.kwargs)
        # print(f"  prompt: {json.dumps(prompt, ensure_ascii=False)}")
        llm_response = self.client.query_one(prompt)
        formated_response = Formater.parse_llm_output_json(llm_response)
        # formated_response = api_info.response_model.model_validate(formated_response)
        print(f"  response: {json.dumps(formated_response, ensure_ascii=False)}")
        return formated_response

    # ------------------------------- 写法1: 无法处理 api_info.request_model = None 的情况 --------------------------------
    # for api_name, api_info in api_registry.registry.items():
    #     @app.post(f"/{api_name}")   # NOTE: skip the response_model checking!   # @app.post(f"/{api_name}", response_model=api_info.response_model)
    #     async def dynamic_api(request: api_info.request_model, api_name=api_name): # type: ignore
    #         # NOTE: 一定要把 api_name 作为变量传入动态函数!
    #         query_info = APICalling_Info(name=api_name, kwargs=request.model_dump())
    #         return mock_api_response(query_info)

    # -------------------------------- 写法2: 使用条件逻辑来动态创建路由处理函数 ----------------------------------------------
    # 辅助函数，用于创建路由处理函数
    def create_dynamic_api(self, api_name, api_info):
        if api_info.request_model:

            async def dynamic_api(request: api_info.request_model):  # type: ignore
                query_info = APICalling_Info(name=api_name, kwargs=request.model_dump())
                return self.mock_api_response(query_info)
        else:

            async def dynamic_api():
                query_info = APICalling_Info(name=api_name)
                return self.mock_api_response(query_info)

        return dynamic_api
