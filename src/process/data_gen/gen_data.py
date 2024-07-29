""" 
gen_PDL_meta_translate.jinja -- 翻译成英文
gen_PDL_extension.jinja -- 进行数据拓展
gen_meta_to_PDL.jinja -- 生成PDL
"""

# %%
import os, sys, json
from process.common import _DIRECTORY_MANAGER

data_metas = []
selected_cols = ["PDL_name", "PDL_description", "PDL_detailed_description"]
for fn in sorted(os.listdir(_DIRECTORY_MANAGER.DIR_data_meta)):
    if not fn.startswith('0'): continue
    meta = json.load(open(f"{_DIRECTORY_MANAGER.DIR_data_meta}/{fn}", "r"))
    data_metas.append({k:v for k,v in meta.items() if k in selected_cols})
print(f"# data_metas: {len(data_metas)}")
# %%
with open(f"{_DIRECTORY_MANAGER.FN_data_meta}", "w") as f:
    json.dump(data_metas, f, indent=4, ensure_ascii=False)



# %%
import tqdm, os, sys, json, yaml
from easonsi import utils
from process.common import _DIRECTORY_MANAGER
from utils.jinja_templates import jinja_render
from engine_v2.common import init_client, LLM_CFG
from easonsi.llm.openai_client import OpenAIClient, Formater

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

# %%
data_metas = json.load(open(f"{_DIRECTORY_MANAGER.FN_data_meta}", "r"))
data_metas_en = []
for meta in tqdm.tqdm(data_metas):
    prompt = jinja_render(
        "gen_PDL_meta_translate.jinja", 
        meta_info=json.dumps(meta, ensure_ascii=False)      # NOTE to dumps to JSON
    )
    llm_response = client.query_one_stream(prompt)
    meta_en = Formater.parse_llm_output_json(llm_response)
    data_metas_en.append(meta_en)

with open(f"{_DIRECTORY_MANAGER.FN_data_meta_en}", "w") as f:
    json.dump(data_metas_en, f, indent=4, ensure_ascii=False)

# %%
data_metas_en = json.load(open(f"{_DIRECTORY_MANAGER.FN_data_meta_en}", "r"))
of = open(_DIRECTORY_MANAGER.FN_data_meta_extension, "a")
for meta in tqdm.tqdm(data_metas_en):
    prompt = jinja_render(
        "gen_PDL_extension.jinja",
        count=4,
        pdl=json.dumps(meta, ensure_ascii=False)
    )
    llm_response = client.query_one_stream(prompt)
    meta_ex = Formater.parse_llm_output_json(llm_response)
    for ex in meta_ex:
        ex["gen_from"] = meta["PDL_name"]
        of.write(json.dumps(ex, ensure_ascii=False) + "\n")
of.close()

# %%

def generate_meta_to_pdl(metas, odir):
    for i,meta in enumerate(tqdm.tqdm(metas)):
        ofn = odir / f"{i:03d}-{meta['PDL_name']}.yaml"
        if ofn.exists(): continue
        prompt = jinja_render(
            "gen_meta_to_PDL.jinja",
            NL=json.dumps(meta, ensure_ascii=False)
        )
        llm_response = client.query_one_stream(prompt)
        pdl = Formater.parse_codeblock(llm_response, type="PDL")
        try:
            yaml.safe_load(pdl)
        except yaml.YAMLError as exc:
            print(exc)
        with open(ofn, "w") as f:
            f.write(pdl)

# data_metas_en = json.load(open(f"{_DIRECTORY_MANAGER.FN_data_meta_en}", "r"))
# odir = _DIRECTORY_MANAGER.DIR_data_base / "../v240628/pdl2_0729"
# generate_meta_to_pdl(data_metas_en, odir)

# data_metas_ex = json.load(open(f"{_DIRECTORY_MANAGER.FN_data_meta_extension}", "r"))
data_metas_ex = utils.LoadJsonl(_DIRECTORY_MANAGER.FN_data_meta_extension)
odir = _DIRECTORY_MANAGER.DIR_data_base / "../v240628/pdl2_0729_ex"
os.makedirs(odir, exist_ok=True)
generate_meta_to_pdl(data_metas_ex, odir)
# %%
