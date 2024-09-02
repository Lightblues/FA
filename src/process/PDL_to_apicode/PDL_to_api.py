""" 
基于PDL中的文字版本 API 来生成后端代码, fake 数据
- [x] 实现基本功能 @240709
- [ ] 将结果合并入 git
- [ ] 修改代码结构: 将多个文件中写成 router 形式, 然后用一个 main.py 提供各类API的调用
"""

import os, tqdm, argparse
from engine import PDL, init_client, LLM_CFG, DataManager, _DIRECTORY_MANAGER
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater

# DIR_apis = _DIRECTORY_MANAGER.DIR_data_base / "apis"

def query_PDL_to_api(client:OpenAIClient, worflow_dir:str, workflow_name:str):
    ofn_code = f"{_DIRECTORY_MANAGER.DIR_api}/{workflow_name}.py"
    ofn_apiinfo = f"{_DIRECTORY_MANAGER.DIR_api}/{workflow_name}.json"
    if os.path.exists(ofn_code):
        print(f"[INFO] {workflow_name} exists!")
        return
    
    pdl = PDL.load_from_file(DataManager.get_workflow_full_path(workflow_name=workflow_name, workflow_dir=worflow_dir))
    pdl_str_for_gen = f"TaskFlowName: {pdl.taskflow_name}\nTaskFlowDesc: {pdl.taskflow_desc}\n\nAPIs: {pdl.apis}\n\nwith paramters: {pdl.slots}"
    prompt = jinja_render("process/pdl/PDL_to_API.jinja", PDL=pdl_str_for_gen)
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
    worflow_dir = "pdl_v0828"
    workflow_names = DataManager.get_workflow_name_list(worflow_dir)
    client = init_client(llm_cfg=LLM_CFG["gpt-4o"])
    for workflow_name in tqdm.tqdm(workflow_names):
        query_PDL_to_api(client, worflow_dir, workflow_name)
        print(f"[INFO] {workflow_name} done!")
