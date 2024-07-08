""" 
基于PDL中的文字版本 API 来生成后端代码, fake 数据
"""

import os
from tqdm import tqdm
from engine_v1.datamodel import PDL
from engine_v1.common import DIR_data, init_client, LLM_CFG, DIR_apis
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater

def prepare_client(model_name="gpt-4o"):
    llm_cfg = LLM_CFG[model_name]
    client = init_client(llm_cfg=llm_cfg)
    return client

def query_PDL_to_api(client:OpenAIClient, workflow_name:str):
    ofn_code = f"{DIR_apis}/{workflow_name}.py"
    ofn_apiinfo = f"{DIR_apis}/{workflow_name}.json"
    if os.path.exists(ofn_code):
        print(f"[INFO] {workflow_name} exists!")
        return
    
    pdl = PDL()
    pdl.load_from_file(f"{DIR_data}/{workflow_name}.txt")
    apis, requests, answers, meta, workflow = pdl.PDL_str.split("\n\n", 4)
    _s_pdl = f"TaskFlowName: {pdl.taskflow_name}\nTaskFlowDesc: {pdl.taskflow_desc}\n\n{apis}"
    prompt = jinja_render("PDL_to_API.jinja", PDL=_s_pdl)
    response = client.query_one_stream(prompt)
    res_code = Formater.parse_codeblock(response, type="python")
    res_apiinfo = Formater.parse_codeblock(response, type="json")
    if not res_code.strip() or not res_apiinfo.strip():
        print(f"[ERROR] {workflow_name} failed!")
        print(f"    response: {response}")
    with open(ofn_code, "w") as f:
        f.write(res_code)
    with open(ofn_apiinfo, "w") as f:
        f.write(res_apiinfo)


if __name__ == '__main__':
    workflow_names = []
    for fn in os.listdir(DIR_data):
        if fn.endswith(".txt"):
            workflow_names.append(fn.rstrip(".txt"))
    workflow_names.sort()
    for workflow_name in tqdm(workflow_names):
        client = prepare_client()
        query_PDL_to_api(client, workflow_name)
        print(f"[INFO] {workflow_name} done!")
