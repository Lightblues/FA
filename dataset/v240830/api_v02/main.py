""" 
1. 设计API schema (definitions)
2. 模拟调用, 这里直接 mock 了
3. 整理API调用形式 (openapi.json), 转换为可解析的形式
"""

from api_registry import api_registry
import api_definitions  # NOTE: to register the apis

import json
from engine import init_client, LLM_CFG
from utils.jinja_templates import jinja_render
from engine.typings import APICalling_Info
from easonsi.llm.openai_client import OpenAIClient, Formater

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

def mock_api_response(query: APICalling_Info):
    print(f"> calling {query.name} with {query.kwargs}")
    api_info = api_registry.get_api_info(query.name)
    api_definition = api_info.to_readable_markdown_api_definition()
    prompt = jinja_render("api_llm_structured.jinja", API=api_definition, api_params=query.kwargs)
    # print(f"  prompt: {json.dumps(prompt, ensure_ascii=False)}")
    llm_response = client.query_one(prompt)
    formated_response = Formater.parse_llm_output_json(llm_response)
    # formated_response = api_info.response_model.model_validate(formated_response)
    print(f"  response: {json.dumps(formated_response, ensure_ascii=False)}")
    return formated_response

from fastapi import FastAPI, Depends
app = FastAPI()
# ------------------------------- 写法1: 无法处理 api_info.request_model = None 的情况 --------------------------------
# for api_name, api_info in api_registry.registry.items():
#     @app.post(f"/{api_name}")   # NOTE: skip the response_model checking!   # @app.post(f"/{api_name}", response_model=api_info.response_model)
#     async def dynamic_api(request: api_info.request_model, api_name=api_name): # type: ignore
#         # NOTE: 一定要把 api_name 作为变量传入动态函数! 
#         query_info = APICalling_Info(name=api_name, kwargs=request.model_dump())
#         return mock_api_response(query_info)

# -------------------------------- 写法2: 使用条件逻辑来动态创建路由处理函数 ----------------------------------------------
# 辅助函数，用于创建路由处理函数
def create_dynamic_api(api_name, api_info):
    if api_info.request_model:
        async def dynamic_api(request: api_info.request_model):
            query_info = APICalling_Info(name=api_name, kwargs=request.model_dump())
            return mock_api_response(query_info)
    else:
        async def dynamic_api():
            query_info = APICalling_Info(name=api_name)
            return mock_api_response(query_info)
    
    return dynamic_api
# 动态创建路由
for api_name, api_info in api_registry.registry.items():
    route = app.post(f"/{api_name}")(create_dynamic_api(api_name, api_info))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, workers=4)

# query = APICalling_Info(
#     name="query_news", kwargs={
#         "news_location": "上海", "news_type": "体育", "news_time": "2024-08-30"
#     }
# )
# res = mock_api_response(query)
# print(res)