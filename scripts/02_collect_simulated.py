""" Collect simulated conversations. @240821
output: https://docs.google.com/spreadsheets/d/1p36xAuhiv9siLo7Lw7bFGk9U33rBBKZOKUetYcLQQt4/edit?gid=1151625617#gid=1151625617
    https://doc.weixin.qq.com/sheet/e3_Aa8AFwbhAEsNvUX5XUlTXSTGWsT5A?scode=AJEAIQdfAAoPxPP2JyAcMATAZtAPI&tab=s2y66m
"""

# %%
import os, json, tqdm, itertools
import pandas as pd

from engine import _DIRECTORY_MANAGER
from easonsi import utils
from easonsi.files.gsheet import GSheet
gsheet = GSheet()

# _ddir = _DIRECTORY_MANAGER.DIR_simulated_base / "template=query_PDL_jinja_pdl=pdl2_step3_model=qwen2_72B_api=llm"
_ddir = _DIRECTORY_MANAGER.DIR_simulated_base / "0822_template=query_PDL_jinja_pdl=pdl2_step3_model=custom_api=llm"
fns = sorted(os.listdir(_ddir))
fns = [fn for fn in fns if fn.endswith(".jsonl")]
workflow_names = [fn[:-len(".jsonl")] for fn in fns]

def sort_file(workflow_name:str):
    # 按照 User_profile 的顺序, 对于生成结果排序
    simulated = utils.LoadJsonl(_ddir / f"{workflow_name}.jsonl")
    uprofiles = utils.LoadJson(_DIRECTORY_MANAGER.DIR_user_profile / f"{workflow_name}.json")
    persona_to_idx = {p["persona"]:i for i,p in enumerate(uprofiles)}
    sorted_data = []
    for _,s in enumerate(simulated):
        for p,idx in persona_to_idx.items():
            if p in s["user_profile"]:
                sorted_data.append((idx, s))
                break
        else:
            raise ValueError(f"Unknown persona: {s['user_profile']}")
    sorted_data = sorted(sorted_data, key=lambda x: x[0])
    assert [d[0] for d in sorted_data[:15]] == list(range(15))
    sorted_data = [d[1] for d in sorted_data]
    assert len(sorted_data) == len(simulated)
    utils.SaveJsonl(sorted_data, _ddir / f"{workflow_name}.jsonl")
    return sorted_data

for workflow_name in tqdm.tqdm(workflow_names):
    sort_file(workflow_name)

# %%
def parse_conv(conversation_s:str):
    convs = []
    role, utterence = None, ""
    for line in conversation_s.split("\n"):
        if not line.strip(): continue
        if line.startswith("[BOT]"):
            if role == "user":
                convs.append(utterence)
                utterence = line
            else:
                if utterence: utterence += "\n"
                utterence += line
            role = "bot"
        elif line.startswith("[USER]"):
            if role == "bot": 
                convs.append(utterence)
                utterence = line
            else:
                if utterence: utterence += "\n"
                utterence += line
            role = "user"
        else:
            if utterence: utterence += "\n"
            utterence += line
    convs.append(utterence)
    return convs

parsed_data = []
for fn in fns:
    data = utils.LoadJsonl(_ddir / fn)
    print(f"{fn}: {len(data)}")
    for i,d in enumerate(data[:10]):            # select first 10!
        parsed_data.append(
            (f'{d["workflow_name"]}_{i:03d}', d["user_profile"])
        )
        conv = parse_conv(d["simulated_conversation"])
        parsed_data.append(("START", conv[0]))
        for j,s in enumerate(conv[1:]):
            role = "USER" if j % 2 == 0 else "BOT"
            parsed_data.append((f"{role}{j//2+1}", s))

df = pd.DataFrame(parsed_data)
df.to_csv(_ddir / "simulated_conversations.csv", index=False)
df

# %%
gsheet.to_gsheet(df, sheet_name="simulated_conversations")





# %%
d = df.iloc[:10,:]
# print(d.to_string())
# %%
from tabulate import tabulate
table_str = tabulate(
    d.values, 
    headers=['round', 'content'], # 'keys'
    tablefmt='psql', 
    maxcolwidths=100
)
print(table_str)



# %%
df.columns = ["round", "content"]
mask = df["round"].str.startswith('0')
# mask
# get index
idx = list(df[mask].index)  + [len(df)]
# %%
import itertools, pickle
def parse_conv(df:pd.DataFrame):
    conversations = []
    
    df.columns = ["round", "content"]
    mask = df["round"].str.startswith('0')
    idx = list(df[mask].index)  + [len(df)]
    for s,e in itertools.pairwise(idx):
        id_, user_profile = df.iloc[s,0], df.iloc[s,1]
        workflow_name, workflow_id = id_.split("_", 1)
        # print(workflow_name, workflow_id)
        conv = df.iloc[s+1:e, :]
        # print(conv)
        conversations.append({
            "workflow_name": workflow_name,
            "workflow_id": int(workflow_id),
            "user_profile": user_profile,
            "simulated_conversation": conv,
        })
    return conversations

conversations = parse_conv(df)
# %%
with open(_ddir / "conversations.pkl", "wb") as f:
    pickle.dump(conversations, f)

# %%
d = conversations[0]
s = tabulate(d["simulated_conversation"], headers="keys", showindex=False, tablefmt='psql', maxcolwidths=100)
print(s)    # ["round", "content"]
# %%