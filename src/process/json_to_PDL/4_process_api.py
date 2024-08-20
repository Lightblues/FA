""" 
纯代码方案见: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/workspace/get_huabu_api/run.py


转换后: name, URL, Method, parameters, response
    {
        "name": "API-新闻查询",
        "description": "查询新闻",
        "parameters": {
            "type": "object",
            "properties": {
                "news_location": {
                    "type": "string",
                    "name": "新闻发生地",
                    "description": "新闻发生地",
                },
                "news_type": {
                    "type": "string",
                    "name": "新闻类型",
                    "enum": ["热搜", "时事"],
                    "description": "新闻类型",
                },
                "news_time": {
                    "type": "string",
                    "name": "新闻时间",
                    "description": "新闻时间",
                }
            },
            "required": ["news_location", "news_type"],
        },
        "response": {
            "type": "object",
            "properties": {
                "news_list": {
                    "type": "array",
                    "name": "查询到的新闻列表",
                    "description": "查询到的新闻列表",
                }
            }
        },
        "URL": "http://11.141.203.151:8089/search_news",
        "Method": "POST"
    }
"""


import os, functools, json
from tqdm import tqdm

from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine_v1.common import DIR_data_base, init_client, LLM_CFG
from utils.jinja_templates import jinja_render
client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

DIR_input = f"{DIR_data_base}/huabu_step0"
DIR_output = f"{DIR_data_base}/apis_v0"
os.makedirs(DIR_output, exist_ok=True)

def collect_node_apis():
    apis = []
    
    data_names = sorted(os.listdir(DIR_input))
    for fn in tqdm(data_names):
        workflow_name, _ = os.path.splitext(fn)
        data = utils.LoadJson(f"{DIR_input}/{fn}")
        print(f"Processing {fn}")
        num_apis = 0
        for node in data["Nodes"]:
            if node["NodeType"] != "API": continue
            api = {
                "from": workflow_name,
                "NodeName": node["NodeName"],
                "ApiNodeData": node["ApiNodeData"],
            }
            apis.append(api)
            num_apis += 1
        print(f"  # apis: {num_apis}")
    print(f"total # apis: {len(apis)}")
    return apis


@functools.lru_cache(None)
def convert_api(api):
    prompt = jinja_render("step4_API.jinja", input=api)
    llm_response = client.query_one(prompt)
    api_converted = Formater.parse_codeblock(llm_response, type="json")
    api_converted = json.loads(api_converted)
    return api_converted

# step1: collect all APIs
fn_raw = f"{DIR_output}/apis_raw.json"
if os.path.exists(fn_raw):
    apis_raw = utils.LoadJson(fn_raw)
else:
    apis_raw = collect_node_apis()
    utils.SaveJson(apis_raw, fn_raw)
    print(f"Saved to {fn_raw}")

# step2: convert the APIs
fn_converted = f"{DIR_output}/apis.json"
apis_converted = []
for api in tqdm(apis_raw):
    apis_converted.append(convert_api(json.dumps(api, ensure_ascii=False)))
utils.SaveJson(apis_converted, fn_converted)

# --- hack ---
# apis_converted = utils.LoadJson(fn_converted)
# for api_raw, api in zip(apis_raw, apis_converted):
#     assert api_raw["NodeName"].lstrip("API-") == api["name"].lstrip("API-")
#     api["from"] = api_raw["from"]
# utils.SaveJson(apis_converted, fn_converted)
# print(f"Saved to {fn_converted}")