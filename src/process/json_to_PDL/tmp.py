
# %%
import os, functools, json, tqdm
import pandas as pd

from easonsi import utils
from easonsi.files.gsheet import GSheet
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine_v1.common import DIR_data_base, init_client, LLM_CFG
from utils.jinja_templates import jinja_render
client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

DIR_input = f"{DIR_data_base}/huabu_step0"
DIR_output = f"{DIR_data_base}/apis_v0"
os.makedirs(DIR_output, exist_ok=True)
pd.__version__
# %%
fn_apis = f"{DIR_output}/apis.json"
apis = utils.LoadJson(fn_apis)

# %%
apis_s = []
for api in apis:
    api["parameters"] = json.dumps(api["parameters"], ensure_ascii=False)
    api["response"] = json.dumps(api["response"], ensure_ascii=False)
    apis_s.append(api)
df = pd.DataFrame(apis_s)
df
# %%
sheet = GSheet()
sheet.to_gsheet(df, sheet_name="apis")

# %%
# df.parameters = json.dumps(df.parameters, ensure_ascii=False)
# df.response = json.dumps(df.response, ensure_ascii=False)
# df.map(lambda x: json.dumps(x, ensure_ascii=False))
# df.parameters = df.parameters.apply(lambda x: json.dumps(x, ensure_ascii=False))
# df.response = df.response.apply(lambda x: json.dumps(x, ensure_ascii=False))
# %%
df.to_excel(f"{DIR_output}/apis.xlsx", index=False)
# %%
