import os, sys, time, datetime, json, ast
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater

_file_dir_path = os.path.dirname(os.path.realpath(__file__))
DIR_data_base = f"{_file_dir_path}/../../data/v240628"
DIR_data = f"{DIR_data_base}/huabu_step3"
DIR_data_meta = f"{DIR_data_base}/huabu_meta"
DIR_log = f"{DIR_data_base}/engine_v1_log"
DIR_simulation = f"{DIR_data_base}/simulation_v01_log"
DIR_simulated = f"{DIR_data_base}/simulated"
DIR_apis = f"{DIR_data_base}/apis_v01"
DIR_conversation = f"{DIR_data_base}/conversation_v01"
FN_data_meta = f"{DIR_data_base}/data_meta.json"

LLM_stop = ["[USER]"]

API_base_url = "http://localhost:8000"
API_infos = []
# register the APIs: search the json files in DIR_apis
for fn in os.listdir(DIR_apis):
    if fn.endswith(".json"):
        with open(f"{DIR_apis}/{fn}", "r") as f:
            # API_infos += json.load(f)     # to avoid ERROR `json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes`
            API_infos += ast.literal_eval(f.read())
            # print(f"[API] registered {fn}!")

LLM_CFG = {
    "SN": {
        "model_name": "神农大模型",
        "base_url": "http://9.91.12.52:8001",
        "api_key": "xxx",
    },
    "gpt-4o": {
        "model_name": "gpt-4o",
        "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
        "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
    }
}
def add_openai_models():
    global LLM_CFG
    import openai
    model_list = ["gpt-4o", "gpt-4-turbo"]
    for model in model_list:
        LLM_CFG[model] = {
            "model_name": model,
            "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
            "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
        }
# add models registered in `/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/model_server/_run_multi_urls.py`
# e.g. WizardLM2-8x22b, qwen2_72B
def add_local_models():
    global LLM_CFG
    import importlib.util
    from urllib.parse import urlparse
    _fn = "/apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/model_server/_run_multi_urls.py"
    spec = importlib.util.spec_from_file_location("model_urls", _fn)
    model_urls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_urls)
    model_info = {}
    for name, url in model_urls.local_urls.items():     # process the `local_urls` object
        if 'http' not in url: continue
        parsed_url = urlparse(url)
        model_info[name] = f"{parsed_url.scheme}://{parsed_url.netloc}"

    for model, url in model_info.items():
        # NOTE: api_key 不能为 "" 不然也会报错
        LLM_CFG[model] = {"model_name": model, "base_url": url, "api_key": "xxx"}
add_local_models()
add_openai_models()
print(f"[INFO] LLM models: {LLM_CFG.keys()}")

def init_client(llm_cfg:Dict):
    # global client
    base_url = os.getenv("OPENAI_PROXY_BASE_URL") if llm_cfg.get("base_url") is None else llm_cfg["base_url"]
    api_key = os.getenv("OPENAI_PROXY_API_KEY") if llm_cfg.get("api_key") is None else llm_cfg["api_key"]
    model_name = llm_cfg.get("model_name", "gpt-4o")
    client = OpenAIClient(
        model_name=model_name, base_url=base_url, api_key=api_key
    )
    return client


class DataManager:
    @staticmethod
    def build_workflow_id_map(config_dir:str, extension:str=".txt"):
        workflow_id_map = {}
        for file in os.listdir(config_dir):
            if file.endswith(extension):
                workflow_name = file.rstrip(extension)
                id, name = workflow_name.split("-", 1)
                workflow_id_map[id] = workflow_name
                workflow_id_map[name] = workflow_name
                workflow_id_map[workflow_name] = workflow_name
        return workflow_id_map
    @staticmethod
    def get_workflow_name_list(config_dir:str, extension:str=".txt"):
        fns = [fn.rstrip(extension) for fn in os.listdir(config_dir) if fn.endswith(extension)]
        return list(sorted(fns))