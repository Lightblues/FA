# %%
import os, json, tqdm, itertools, pickle, collections, itertools
import pandas as pd
import concurrent.futures
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL
from utils.jinja_templates import jinja_render
from tabulate import tabulate

from judge_util import VERSION

_ddir = _DIRECTORY_MANAGER.DIR_simulated_base / VERSION
fn_conversations = _ddir / "conversations.pkl"
fn_humanscored = _ddir / "【数据标注】【任务型标品PDL】测试数据标注 240822-v240822.csv"
fn_humanscored_eval = _ddir / "conversations_eval_human.jsonl"
# --- structure of fn_llmscored ---
# {workflow_name, workflow_id, judge_result, infos}
#   judge_result: {overall: {score}, detailed: [{round-i: {errors: [{}], score}}]}
#   infos: {prompt, response, user_profile}

df = pd.read_csv(fn_humanscored)
# remove first column
df = df.iloc[:,1:]
df = df.astype(object)      # # 将数据框中的数据类型转换为 Python 本地数据类型, int64 --> int

# %%
# ===================================================================================
#                               basic analysis
# df["错误类型"].value_counts()
cnt = collections.Counter()
for errors in df["错误类型"]:
    if type(errors)==str:
        for e in errors.split(","):
            cnt[e.strip()] += 1
cnt
# %%
cnt = collections.Counter()
for idx, row in df.iterrows():
    if row["序号"].startswith("0"):
        cnt[row["满意度"]] += 1
cnt


# %%
# ===================================================================================
#                               convert to fn_llmscored
# df.columns  # Index(['序号', 'conv01', '错误类型', '满意度', '评分理由'], dtype='object')
_mask = df["序号"].str.startswith('0')
idxs = list(df[_mask].index)  + [len(df)]
result = []
for s,e in itertools.pairwise(idxs):
    subdf = df.iloc[s:e, :].reset_index()
    workflow_name, workflow_id = subdf["序号"][0].split("_", 1)
    overall = {
        "score": subdf["满意度"][0],
        "comment": subdf["评分理由"][0],
    }
    detailed = {}
    for idx in range(3, len(subdf), 2):
        _idx = f"round-{idx//2}"
        d = {
            "score": subdf["满意度"][idx],
            "errors": {},
        }
        _e = subdf["错误类型"][idx]
        if type(_e)==str and _e:
            for e in _e.split(","):
                d["errors"][e] = subdf["评分理由"][idx]
        detailed[_idx] = d
    result.append({
        "workflow_name": workflow_name,
        "workflow_id": int(workflow_id),
        "judge_result": {
            "overall": overall,
            "detailed": detailed,
        },
    })
utils.SaveJsonl(result, fn_humanscored_eval)
# %%
