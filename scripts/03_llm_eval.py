

# %%
import os, json, tqdm, itertools, pickle
import pandas as pd
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL
from utils.jinja_templates import jinja_render
from tabulate import tabulate

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

# %%
_ddir = _DIRECTORY_MANAGER.DIR_simulated_base / "template=query_PDL_jinja_pdl=pdl2_step3_model=qwen2_72B_api=llm"
with open(_ddir / "conversations.pkl", "rb") as f:
    conversations = pickle.load(f)
# %%
conv = conversations[0]
workflow_name = conv["workflow_name"]
pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu_step3 / f"{workflow_name}.yaml")
pdl
# %%
conv = conversations[5]
s_conv = tabulate(conv["simulated_conversation"], headers="keys", showindex=False, tablefmt='psql', maxcolwidths=100)
prompt = jinja_render(
    "scorer_detailed.jinja",
    conversation=s_conv,
    PDL=pdl.to_str(),
)
print(prompt)
res = client.query_one_stream(prompt)
# %%
