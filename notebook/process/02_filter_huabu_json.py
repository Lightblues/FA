""" 
过滤逻辑:
1. 去除过长过短的数据
2. 泛化性较差的数据 (过于specific)

保留数据: —— 保证得到数据的分布均衡
1. 节点类别: 自动判定类别? 
2. 难易程度: 根据节点数量、分支数量、JSON长度等来区分
"""

# %%
import os, json
import pandas as pd
from tqdm import tqdm
from easonsi import utils
DIR_data = f"../../data/画布json-v240627"
DIR_input = f"{DIR_data}/json_step0"

# %%
fns = os.listdir(DIR_input)
fns.sort()
fns[:5]

# %%
data = utils.LoadJson(f"{DIR_input}/{fns[0]}")
data

# %%
def get_stat(d: dict):
    info = {
        "TaskFlowID": d["TaskFlowID"],
        "TaskFlowName": d["TaskFlowName"],
        'TaskFlowDesc': d.get('TaskFlowDesc', ''),
        "JSONLength": len(json.dumps(d)),
        "NodeCount": len(d["Nodes"]),
        "EdgeCount": len(d["Edges"]),
        "BranchesTotalCount": 0,
        "BranchesAvgCount": 0,
        "BranchesMaxCount": 0,
    }
    nodes = d["Nodes"]
    branches_cnt = []
    for node in nodes:
        branches = node.get("Branches", [])
        branches_cnt.append(len(branches))
    info["BranchesTotalCount"] = sum(branches_cnt)
    info["BranchesAvgCount"] = info["BranchesTotalCount"] / len(nodes)
    info["BranchesMaxCount"] = max(branches_cnt)

    edges = d["Edges"]
    return info

infos = get_stat(data)
def print_info(info, d):
    # print the infos
    print(f"=== {d['TaskFlowName']} ===")
    for k, v in info.items():
        if type(v) in [float]:
            v = round(v, 2)
        print(f"{k}: {v}")

# %%
datas = [utils.LoadJson(f"{DIR_input}/{fn}") for fn in fns]

# %%
infos = [get_stat(d) for d in datas]

# %%
n_samples = 5
for d, info in zip(datas[:n_samples], infos[:n_samples]):
    print_info(info, d)

# %%
infos_df = pd.DataFrame(infos)
infos_df.reset_index(inplace=True)
infos_df

# %%
infos_df.to_csv(f"{DIR_data}/infos/json_step1_infos.csv", index=False)
# %%
from easonsi.files.gsheet import GSheet
gsheet = GSheet()
gsheet.to_gsheet(infos_df, sheet_name="json_step1_infos")

# %%
