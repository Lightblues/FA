
# %%
import os, json, tqdm, itertools
import pandas as pd

from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from utils.jinja_templates import jinja_render
from engine import PDL

workflow_name = "000-114挂号"

pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu_step3 / f"{workflow_name}.yaml")
# print(pdl.to_str())

# %%
_ddir = _DIRECTORY_MANAGER.DIR_simulated_base / "template=query_PDL_jinja_pdl=pdl2_step3_model=qwen2_72B_api=llm"
data = utils.LoadJsonl(_ddir / f"{workflow_name}.jsonl")

d = data[0]
# print(d["simulated_conversation"])

# %%
prompt = jinja_render(
    "scorer.jinja",
    conversation=d["simulated_conversation"],
    PDL=pdl.to_str(),
)
print(prompt)
# %%
client = init_client(LLM_CFG["gpt-4o"])
res = client.query_one_stream(prompt)
# %%
