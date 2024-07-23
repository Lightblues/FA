""" Collect simulated conversations.
output: https://docs.google.com/spreadsheets/d/1p36xAuhiv9siLo7Lw7bFGk9U33rBBKZOKUetYcLQQt4/edit?gid=1151625617#gid=1151625617
"""

import os, json, tqdm
import pandas as pd

from engine_v2.common import DIR_simulated_base
from easonsi.files.gsheet import GSheet

gsheet = GSheet()

dir_simulated = DIR_simulated_base / "template=query_PDL_v04_jinja_pdl=huabu_step3_model=qwen2_72B_api=v01"

data_simulated = []
fns = sorted(os.listdir(dir_simulated))
for fn in tqdm.tqdm(fns):
    with open(dir_simulated / fn, "r") as f:
        data = json.load(f)
    for d in data:
        d['meta_infos'] = json.dumps(d['meta_infos'], ensure_ascii=False)
    data_simulated.extend(data)
df_simulated = pd.DataFrame(data_simulated)
gsheet.to_gsheet(df_simulated, sheet_name="simulated_conversations")