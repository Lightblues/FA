""" 给定 PDL 生成流程描述
@240715

"""

import json, os
from tqdm import tqdm
from utils.jinja_templates import jinja_render
from engine_v1.datamodel import PDL
from engine_v1.common import DIR_data, init_client, LLM_CFG, DIR_apis, DIR_data_base, DIR_data_meta
from easonsi.llm.openai_client import OpenAIClient, Formater

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

# workflow_name = "000-114挂号"
# workflow_name = "002-新闻查询"
def gen_NL(client: OpenAIClient, workflow_name: str):
    ofn = f"{DIR_data_meta}/{workflow_name}.json"
    if os.path.exists(ofn):
        print(f"[INFO] {workflow_name} exists! return!")
        return
    pdl = PDL()
    pdl.load_from_file(f"{DIR_data}/{workflow_name}.txt")
    prompt = jinja_render("PDL_to_NL.jinja", PDL=pdl.PDL_str)
    # print(prompt)

    res = client.query_one_stream(prompt)
    r = Formater.parse_codeblock(res, type="json")
    r = json.loads(r)
    with open(ofn, "w") as f:
        json.dump(r, f, indent=4, ensure_ascii=False)
    return r

if __name__ == '__main__':
    workflow_names = []
    for fn in os.listdir(DIR_data):
        if fn.endswith(".txt"):
            workflow_names.append(fn.rstrip(".txt"))
    workflow_names.sort()
    for workflow_name in tqdm(workflow_names):
        gen_NL(client, workflow_name)
        print(f"[INFO] {workflow_name} done!")
        
# # %%
# from engine_v1.common import DIR_data, init_client, LLM_CFG, DIR_apis, DIR_data_base, DIR_data_meta
# import json, os
# data_meta = []
# for fn in sorted(os.listdir(DIR_data_meta)):
#     if fn.endswith(".json"):
#         workflow_name = fn.rstrip(".json")
#         with open(f"{DIR_data_meta}/{fn}", "r") as f:
#             meta = {"id": workflow_name}
#             meta.update(json.load(f))
#             data_meta.append(meta)

# with open(f"{DIR_data_base}/data_meta.json", "w") as f:
#     json.dump(data_meta, f, indent=4, ensure_ascii=False)
# # %%
