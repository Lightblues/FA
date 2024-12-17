"""
利用LLM自动化地将API转为后端代码
see [PDL_2_apicode]
"""

# %%
import os


_file_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(f"{_file_dir}/../../src")
# DIR_data = "../../data/v240628/huabu_step3/"
from engine_v1.common import DIR_data
from engine_v1.datamodel import PDL


template_v01 = """Please mock some data and write a `fastapi` backend for the following apis, please also include test cases for each api with package `requests`.
NOTE to keep the function and parameter names!

Here are the natural language format APIs:
```PDL
{PDL}
```

Please give your code below:
"""

template = """Please mock some data and write a `fastapi` backend for the following apis, NOTE to
1. keep the function and parameter names!
2. just use sync version of FastAPI, and you need to write the Request and Response models in the code!
3. also output the corresponding API infos in the following format:
```json
[
    {{
        "name": "通过交易金额查询",
        "type": "POST",
        "endpoint": "/query_by_amount",
        "request": ["amount"],
        "response": ["order_links"],
        "request_zh": ["交易金额"],
        "response_zh": ["订单编号超链"],
    }}
]
```

Here are the natural language format APIs:
```PDL
{PDL}
```

Please give your answer below:
"""

pdl = PDL()
# workflow_name = "022-挂号"
workflow_name = "004-服务网点查询"
pdl.load_from_file(f"{DIR_data}/{workflow_name}.txt")
apis, requests, answers, meta, workflow = pdl.PDL_str.split("\n\n")
_s_pdl = f"TaskFlowName: {pdl.taskflow_name}\nTaskFlowDesc: {pdl.taskflow_desc}\n\n{apis}"
prompt = template.format(PDL=_s_pdl)
print(prompt)


# %%
import os

from engine_v1.common import init_client


# llm_cfg = {
#     "model_name": "神农大模型",
#     "base_url": "http://9.91.12.52:8001",
#     "api_key": "xxx",
# }
llm_cfg = {
    "model_name": "gpt-4o",
    "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
    "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
}
# client = OpenAIClient(**llm_cfg)
client = init_client(llm_cfg=llm_cfg)
response = client.query_one_stream(prompt)


# %%
""" I have the following APIs:
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

corresponding FastAPI code:
@app.post("/query_by_amount", response_model=QueryByAmountResponse)
def query_by_amount(request: QueryByAmountRequest):
    order_links = [f"/orders/{order['order_id']}" for order in mock_orders if order["amount"] == request.amount]
    if not order_links:
        raise HTTPException(status_code=404, detail="No orders found with the specified amount")
    return QueryByAmountResponse(order_links=order_links)

@app.post("/query_by_time", response_model=QueryByTimeResponse)
def query_by_time(request: QueryByTimeRequest):
    order_links = [f"/orders/{order['order_id']}" for order in mock_orders if order["transaction_time"] == request.transaction_time]
    if not order_links:
        raise HTTPException(status_code=404, detail="No orders found with the specified transaction time")
    return QueryByTimeResponse(order_links=order_links)

@app.post("/query_by_order_id", response_model=QueryByOrderIdResponse)
def query_by_order_id(request: QueryByOrderIdRequest):
    order = next((order for order in mock_orders if order["order_id"] == request.order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="No orders found with the specified order ID")
    return QueryByOrderIdResponse(details=order["details"])

Please write a function for me
```python
def call_py_name_and_paras(api_name:str, api_paras:List[str]):
    # call_py_name_and_paras("通过交易时间查询", ["2024-06-01"])
    ...
```


"""
