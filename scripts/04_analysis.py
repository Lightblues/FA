""" ================= moved to @evaluator.py ==================== """

# %%
import os, json, tqdm, itertools, pickle, collections
from typing import List, Dict, Optional, Tuple
import pandas as pd
import concurrent.futures
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL
from utils.jinja_templates import jinja_render
from tabulate import tabulate

from judge_util import VERSION

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

_ddir = _DIRECTORY_MANAGER.DIR_simulation / VERSION
fn_conversations = _ddir / "conversations.pkl"
fn_llmscored = _ddir / "conversations_eval_gpt.jsonl"
fn_humanscored = _ddir / "conversations_eval_human.jsonl"
# --- structure of fn_llmscored ---
# [workflow_name, workflow_id, judge_result, infos]
#   judge_result: {overall: {score}, detailed: [{round-i: {errors: [{}], score}}]}
#   infos: {prompt, response, user_profile}

df_gpt = pd.read_json(fn_llmscored, lines=True)
# df_human = pd.read_json(fn_humanscored, lines=True)

# %%
# df = df_human
df = df_gpt

def stat_num_rounds(df: pd.DataFrame):
    df["num_rounds"] = df["judge_result"].apply(lambda x: len(x["detailed"]))
    avg_conv_turns = df["num_rounds"].mean()
    print(f"avg num rounds: {avg_conv_turns:.2f}")
    
    vc_num_rounds = df["num_rounds"].value_counts().sort_index().reset_index()
    return vc_num_rounds

_ = stat_num_rounds(df)

# %%
def stat_scores_overall(df: pd.DataFrame, th=4):
    df['overall_score'] = df['judge_result'].apply(lambda x: x["overall"]["score"])
    mean_score = df["overall_score"].mean()
    passrate = sum(df["overall_score"] >= th) / len(df)
    print(f"Mean score: {mean_score:.2f}\nPassrate: {passrate:.2f}")
    
    df_scores = df['overall_score'].value_counts().sort_index().reset_index()
    return df_scores
_ = stat_scores_overall(df)


# %%
def stat_error_types(df: pd.DataFrame):
    cnt = collections.Counter()
    for idx, row in df.iterrows():
        # print(f"{row['workflow_name']} - {row['workflow_id']}")
        for round_id, round_eval in row['judge_result']["detailed"].items():
            if not round_eval["errors"]: continue
            try:
                for error_type, error_reason in round_eval["errors"].items():
                    # print(f"  {round_id}: {error_type} {error_reason}")
                    cnt[error_type] += 1
            except Exception as e:
                print(round_eval["errors"])
    return cnt
cnt = stat_error_types(df_gpt)
cnt

# %%
def stat_grouped_passrate(df: pd.DataFrame, th=4):
    df['overall_score'] = df['judge_result'].apply(lambda x: x["overall"]["score"])
    # df["workflow_name", "overall_score"]
    def calculate_ratio(group):
        total = len(group)
        above_3 = len(group[group['overall_score'] >= th])
        return above_3 / total
    ratios = df.groupby('workflow_name').apply(calculate_ratio).reset_index()
    ratios.columns = ['workflow_name', 'ratio']
    return ratios

stat_grouped_passrate(df_gpt)

# %%
print(tabulate(df_gpt.iloc[:5,:], showindex=False, headers="keys"))  # , tablefmt='psql'

# %%
def get_detailed_score_pairs(df_gpt: pd.DataFrame, df_human: pd.DataFrame) -> List[Tuple[float, float]]:
    gpt_scores = df_gpt['judge_result'].apply(lambda x: [v['score'] for k, v in x['detailed'].items()])
    human_scores = df_human['judge_result'].apply(lambda x: [v['score'] for k, v in x['detailed'].items()])

    score_pairs = []
    for gpt_score_list, human_score_list in zip(gpt_scores, human_scores):
        for gpt_score, human_score in zip(gpt_score_list, human_score_list):
            score_pairs.append((gpt_score, human_score))

    return score_pairs
