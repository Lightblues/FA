""" 
利用LLM自动化地将API转为后端代码
"""

# %%
template = """Please mock some data and write a `fastapi` backend for the following apis, please also include test cases for each api with package `requests`.
NOTE to keep the function and parameter names! 

Here are the natural language format APIs:
```PDL
{PDL}
```

Please give your code below:
"""

API_PDL = """TaskFlowName: 银行订单查询
APIs:
-
    name: API-通过交易金额查询
    request: [交易金额]
    response: [订单编号超链]
-
    name: API-通过交易时间查询
    request: [交易时间]
    response: [订单编号超链]
-
    name: API-通过订单编号查询
    request: [订单编号]
    response: [订单详情]
"""

prompt = template.format(PDL=API_PDL)
print(prompt)

# %%
from engine_v1.common import init_client
from easonsi.llm.openai_client import OpenAIClient, Formater
llm_cfg = {
    "model_name": "神农大模型",
    "base_url": "http://9.91.12.52:8001",
    "api_key": "xxx",
}
# client = OpenAIClient(**llm_cfg)
client = init_client(llm_cfg=llm_cfg)
response = client.query_one_stream(prompt)
# %%
