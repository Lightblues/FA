""" 
@240729 根据已有的API生成数据
"""

# %%
import os, json, tqdm
from utils.jinja_templates import jinja_render
from engine.common import init_client, LLM_CFG
from easonsi.llm.openai_client import OpenAIClient, Formater

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

apis = """APIs:
-
    name: 校验挂号医院
    request: [hos_name]
    response: [医院存在类型]
    precondition: []
-
    name: 科室校验
    request: [keshi_name, hos_name]
    response: [科室存在状态]
    precondition: ['校验挂号医院']
-
    name: 指定时间号源查询
    request: [hos_name, keshi_name, t_time]
    response: [可挂号数量, 可挂号列表, 专家号数量, 普通号数量]
    precondition: ['科室校验']
-
    name: 其他医院号源推荐
    request: [keshi_name, t_time]
    response: [号源数量, 医院名称, 挂号医生]
    precondition: ['指定时间号源查询']
-
    name: 本医院挂号执行
    request: [id_num, num_type, hos_name, keshi_name, t_time]
    response: [挂号状态]
    precondition: ['指定时间号源查询']
-
    name: 挂号执行
    request: [id_num, hos_name, doc_name]
    response: [挂号状态]
    precondition: ['其他医院号源推荐']"""

prompt = jinja_render(
    "gen_db_with_apis.jinja",
    apis=apis,
)
# print(prompt)
llm_response = client.query_one_stream(prompt)
# print(llm_response)


# %%
