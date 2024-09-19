""" 数据生成全流程. (需要原始数据: apis, NL/PDL format workflow, seed persona)
1. convert API
2. build "task_infos.json"
3. convert formats
    PDL -> NL
    NL -> other formats
4. user profiles
"""

# %%
import os, sys, json, yaml, pathlib, tqdm

IDIR = pathlib.Path("/work/huabu/dataset/v240830")
ODIR = pathlib.Path("/work/huabu/dataset/PDL")
os.makedirs(ODIR, exist_ok=True)

def build_name_map(subdir="pdl"):
    fns = os.listdir(IDIR / subdir)
    fns.sort()
    # remove the extension
    names = [os.path.splitext(fn)[0] for fn in fns]
    _map = {name: f"{i:03d}" for i, name in enumerate(names)}
    return _map
name_map = build_name_map("api_v02/api_schemas")
print(f"#pdls: {len(name_map)}")

# %%
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine import init_client, LLM_CFG
from data_utils.workflow_format.format_transformer import FormatTransformer, APITransformer

def transform_api_format(api):
    llm = init_client(llm_cfg=LLM_CFG["gpt-4o"])
    
    prompt = jinja_render(
        "data_utils/transform_api_format.jinja",
        API=json.dumps(api, indent=2)
    )
    llm_resp = llm.query_one(prompt)
    
    transformed_api = Formater.parse_llm_output_json(llm_resp)
    return transformed_api

def convert_format_api(subdir="api_v02/api_schemas"):
    print(f"Converting api from `{subdir}` subfolder")
    os.makedirs(ODIR / "tools", exist_ok=True)
    num_success = 0
    for name in tqdm.tqdm(name_map):
        try:
            _ofn = ODIR / "tools" / f"{name_map[name]}.yaml"
            if os.path.exists(_ofn):
                continue

            with open(IDIR / subdir / f"{name}.json", "r") as f:
                data = json.load(f)
            converted_api = transform_api_format(data)
            with open(_ofn, "w") as f:
                yaml.dump(converted_api, f, indent=2, allow_unicode=True)
            num_success += 1
        except Exception as e:
            print(f"Error for {name}: {e}")
            continue
    print(f"Converted {num_success} tasks")
    return num_success

convert_format_api()

# %%
llm = init_client(llm_cfg=LLM_CFG["gpt-4o"])
def covert_to_NL(subdir="pdl"):
    print(f"Converting NL from `{subdir}` subfolder")
    os.makedirs(ODIR / "_text", exist_ok=True)
    for name, id in tqdm.tqdm(name_map.items()):
        _ofn = ODIR / "_text" / f"{id}.json"
        if os.path.exists(_ofn): continue

        with open(IDIR / subdir / f"{name}.yaml", "r") as f: pdl = f.read()
        
        prompt = jinja_render(
            "data_utils/pseudo_to_NL.jinja",
            pseudo=pdl
        )
        llm_resp = llm.query_one(prompt)
        res = Formater.parse_llm_output_json(llm_resp)
        with open(_ofn, "w") as f: 
            json.dump(res, f, indent=2, ensure_ascii=False)

covert_to_NL()

# %%
def build_task_infos(subdir="_text", version="v240908"):
    task_infos = {}
    
    os.makedirs(ODIR / "text", exist_ok=True)
    for name, id in tqdm.tqdm(name_map.items()):
        with open(ODIR / subdir / f"{id}.json", "r") as f: 
            task_info = json.load(f)
        # task_info = 
        task_infos[id] = {
            "name": task_info["task_name"],
            "task_background": task_info["task_description"],
        }
        with open(ODIR / "text" / f"{id}.txt", "w") as f: 
            f.write(task_info["task_detailed_description"])
    result = {
        "version": version,
        "task_infos": task_infos
    }
    with open(ODIR / "task_infos.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return task_infos
task_infos = build_task_infos()


# %%
format_to_codeblock = {
    "PDL": "PDL",
    "code": "python",
    "CoRE": "CoRE",
    "flowchart": "mermaid"
}
format_to_suffix = {
    "PDL": "txt",
    "code": "py",
    "CoRE": "txt",
    "flowchart": "md"
}
def transform_NL_to_other_format(target_format):
    """ 
    see src/data_utils/workflow_format/transform_format.py
    """
    NL_transformer = FormatTransformer("gpt-4o", f"data_utils/NL_to_{target_format}.jinja", return_format=format_to_codeblock[target_format])
    
    for task in tqdm.tqdm(name_map.values()):
        with open(ODIR / f"_text/{task}.json", 'r', encoding='utf-8') as f:
            task_desc = json.load(f)
        with open(ODIR / f"tools/{task}.yaml", 'r', encoding='utf-8') as f:
            apis = yaml.load(f, Loader=yaml.FullLoader)
            
        transformed_workflow = NL_transformer.transform(NL_desc=task_desc, apis=apis)
        file_suffix = format_to_suffix[target_format]
        os.makedirs(ODIR / f"{target_format}", exist_ok=True)
        with open(ODIR / f"{target_format}/{task}.{file_suffix}", 'w', encoding='utf-8') as f:
            f.write(transformed_workflow)

# transform_NL_to_other_format("code")
transform_NL_to_other_format("flowchart")

# %%
import re, random
from easonsi import utils

llm = init_client(llm_cfg=LLM_CFG["gpt-4o"])
def create_user_profiles(task_desc, personas):
    """ 
    see src/data_utils/user_profiles/create_profile.py
    """
    profiles = []
    for persona in tqdm.tqdm(personas):
        prompt = jinja_render(
            'data_utils/persona_to_profile2.jinja',
            Task_Description=task_desc,
            Persona=persona
        )
        llm_resp = llm.query_one(prompt)
        split_resp = re.findall(r'\d\..*?:', llm_resp)
        assert len(split_resp) == 5
        split_idx = [(llm_resp.find(split), llm_resp.find(split) + len(split)) for split in split_resp]
        split_info = []
        for i in range(len(split_resp) - 1):
            split_info.append(llm_resp[split_idx[i][1]: split_idx[i + 1][0]])
        split_info.append(llm_resp[split_idx[-1][1]:])
        user_details = split_info[0].strip()
        user_needs = split_info[1].strip()
        _apis = split_info[2].strip()
        _apis = _apis.split(',')
        required_apis = [api.strip() for api in _apis]
        dialogue_style = split_info[3].strip()
        interative_pattern = split_info[4].strip()
        
        user_profile = {
            'persona': persona,
            'user_details': user_details,
            'user_needs': user_needs,
            'required_apis': required_apis,
            'dialogue_style': dialogue_style,
            'interative_pattern': interative_pattern
        }
        profiles.append(user_profile)
    os.makedirs(ODIR / 'user_profile', exist_ok=True)
    with open(ODIR / f'user_profile/{task}.json', 'w') as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

fn_persona = "/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/data/persona-hub/persona_expanded.jsonl"
personas = utils.LoadJsonl(fn_persona)
personas = [p["persona"] for p in personas]
for task in name_map.values():
    with open(ODIR / f"_text/{task}.json", 'r', encoding='utf-8') as f:
        task_desc = json.load(f)
    task_desc_str = "\n".join(f"{k}: {v}" for k, v in task_desc.items())
    with open(ODIR / f"tools/{task}.yaml", 'r', encoding='utf-8') as f:
        apis = yaml.load(f, Loader=yaml.FullLoader)
    task_desc_str += "\n\nAPIs: " + yaml.dump(apis, indent=2, allow_unicode=True)
    selected_personas = random.sample(personas, 15)
    
    print(f'processing the personas for task: {task}')
    create_user_profiles(task_desc_str, selected_personas)

# %%
