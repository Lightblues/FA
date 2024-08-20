
# %%
import os, sys, json, tqdm, yaml
from process.common import _DIRECTORY_MANAGER
from utils.jinja_templates import jinja_render
from engine_v2.common import init_client, LLM_CFG
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

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

# %%
fns = os.listdir(_DIRECTORY_MANAGER.DIR_pdl1_step3)
fns.sort()
names = [os.path.splitext(fn)[0] for fn in fns]

# %%
os.makedirs(_DIRECTORY_MANAGER.DIR_pdl2_step3, exist_ok=True)
for name in tqdm.tqdm(names):
    fn = _DIRECTORY_MANAGER.DIR_pdl1_step3 / f"{name}.txt"
    ofn = _DIRECTORY_MANAGER.DIR_pdl2_step3 / f"{name}.yaml"
    prompt = jinja_render(
        "PDL_convert_to_v2.jinja",
        PDL_v1=open(fn).read()
    )
    response = client.query_one_stream(prompt)
    pdl = Formater.parse_codeblock(response, type="PDL")
    try:
        yaml.safe_load(pdl)
    except yaml.YAMLError as exc:
        print(exc)
    with open(ofn, "w") as f:
        f.write(pdl)

# %%
def check_pdl_v2(pdl: dict):
    assert set(pdl.keys()) == set("Name Desc SLOTs APIs ANSWERs PDL".split()), f"ERROR keys: {pdl.keys()}"
data = []
for name in tqdm.tqdm(names):
    with open(_DIRECTORY_MANAGER.DIR_pdl1_step3 / f"{name}.txt") as f:
        pdl_v1 = f.read()
    with open(_DIRECTORY_MANAGER.DIR_pdl2_step3 / f"{name}.yaml") as f:
        pdl_v2 = f.read()
    pdl = yaml.safe_load(pdl_v2)
    check_pdl_v2(pdl)
    data.append({
        "PDL_name": name,
        "PDL_v1": pdl_v1,
        "PDL_v2": pdl_v2,
        **pdl
    })
# %%
import pandas as pd
df = pd.DataFrame(data)
# %%
df.to_excel("pdl_v2.xlsx")
# %%
