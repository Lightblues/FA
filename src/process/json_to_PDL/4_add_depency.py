
# %%
import os, functools, json
from tqdm import tqdm

from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine import (
    _DIRECTORY_MANAGER, init_client, LLM_CFG,
    DataManager, PDL
)
from utils.jinja_templates import jinja_render
client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

@functools.lru_cache(None)
def build_dependency(pdl):
    prompt = jinja_render("step5_PDL_dependency.jinja", PDL=pdl)
    llm_response = client.query_one(prompt)
    res = Formater.parse_codeblock(llm_response, type="json")
    res = json.loads(res)
    return res

def convert_dependency(name):
    fn = _DIRECTORY_MANAGER.DIR_huabu / f"{name}.txt"
    with open(fn, 'r') as f:
        pdl = f.read()
    res = build_dependency(pdl)
    return res

def add_meta(list_dependency):
    for name in names:
        ofn = _DIRECTORY_MANAGER.DIR_data_base / f"huabu_meta/{name}.json"
        meta = {} if not os.path.exists(ofn) else json.load(open(ofn, "r"))
        if "dependency" not in meta:
            meta["dependency"] = list_dependency[name]
        with open(ofn, "w") as f:
            json.dump(meta, f, indent=4, ensure_ascii=False)




# %%
names = DataManager.get_workflow_name_list(_DIRECTORY_MANAGER.DIR_huabu)

ofn = _DIRECTORY_MANAGER.DIR_data_base / "huabu_meta/_dependency_v01.json"
if os.path.exists(ofn):
    list_dependency = json.load(open(ofn))
else:
    list_dependency = {}
    for name in tqdm(names):
        res = convert_dependency(name)
        list_dependency[name] = res
    # save the denpency information to $meta
    utils.SaveJson(list_dependency, ofn)
    add_meta(list_dependency)



# %%
def add_dependency(name):
    pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu / f"{name}.txt")
    name2node = {}
    api_names = [i['name'] for i in pdl.apis]
    answer_names = [i['name'] for i in pdl.answers]
    for n in pdl.apis + pdl.answers:
        name2node[n['name']] = n
    used_names = api_names + answer_names
    
    depends = list_dependency[name]
    for d in depends:
        if d["type"] not in ["API", "ANSWER"]: continue
        preconditions = [n for n in d["dependencies"] if n in used_names]
        name2node[d["name"]]["precondition"] = preconditions
    pdl_converted = pdl.to_str(use_raw=False)
    ofn = _DIRECTORY_MANAGER.DIR_data_base / "huabu_step3_v01" / f"{name}.txt"
    with open(ofn, "w") as f:
        f.write(pdl_converted)
for name in tqdm(names):
    add_dependency(name)
# %%
