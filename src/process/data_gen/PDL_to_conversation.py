""" 
利用LLM自动化地构造数据
@easonsshi 240709
"""
import os, json
from tqdm import tqdm
from engine_v1.datamodel import PDL
from engine_v1.common import DIR_data, init_client, LLM_CFG, DIR_apis, DIR_data_base
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import Formater, OpenAIClient

client = init_client(llm_cfg=LLM_CFG["gpt-4-turbo"])

def gen_conversation_with_PDL(client: OpenAIClient, workflow_name):
    ofn = f"{DIR_data_base}/conversation_v01/{workflow_name}.json"
    assert os.path.exists(os.path.dirname(ofn))
    if os.path.exists(ofn):
        data = json.load(open(ofn))
    else:
        data = []
    
    pdl = PDL()
    pdl.load_from_file(f"{DIR_data}/{workflow_name}.txt")
    prompt = jinja_render("PDL_to_conversation_gen.jinja", PDL=pdl.PDL_str, n=3)    # TODO: change n adaptively
    res = client.query_one_stream(prompt)
    r = Formater.parse_codeblock(res, type="json")
    r = json.loads(r)
    data += r
    with open(ofn, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    workflow_names = []
    for fn in os.listdir(DIR_data):
        if fn.endswith(".txt"):
            workflow_names.append(fn.rstrip(".txt"))
    workflow_names.sort()
    for workflow_name in tqdm(workflow_names):
        gen_conversation_with_PDL(client, workflow_name)
        print(f"[INFO] {workflow_name} done!")
