""" ================= moved to @evaluator.py ==================== """

# %%
import os, json, tqdm, itertools, pickle, collections
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
fn_llmscored_raw = _ddir / "conversations_eval_gpt_raw.jsonl"
# --- structure of fn_llmscored ---
# [workflow_name, workflow_id, judge_result, infos]
#   judge_result: {overall: {score}, detailed: [{round-i: {errors: [{}], score}}]}
#   infos: {prompt, response, user_profile}

# %%
def task(conv, ofn):
    workflow_name = conv["workflow_name"]
    pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu / f"{workflow_name}.yaml")
    s_conv = tabulate(conv["simulated_conversation"], headers="keys", showindex=False, tablefmt='psql', maxcolwidths=100)
    prompt = jinja_render(
        "scorer_detailed.jinja",
        conversation=s_conv,
        PDL=pdl.to_str(),
    )
    res = client.query_one(prompt)
    res_formatted = Formater.parse_llm_output_yaml(res)
    if "error" in res_formatted:
        return 1
    out = {
        "workflow_name": workflow_name,
        "workflow_id": conv["workflow_id"],
        "judge_result": res_formatted,
        "infos": {
            "prompt": prompt,
            "response": res,
            "user_profile": conv["user_profile"]
        }
    }
    with open(ofn, "a") as f:
        f.write(json.dumps(out, ensure_ascii=False) + "\n")
    return 0

def llm_eval(conversations, max_workers=20):
    skipped = set()
    if os.path.exists(fn_llmscored_raw):
        existed = utils.LoadJsonl(fn_llmscored_raw)
        for d in existed:
            skipped.add((
                d["workflow_name"], d["workflow_id"]
            ))
    conversations_filtered = [c for c in conversations if (c["workflow_name"], c["workflow_id"]) not in skipped]
    print(f"# of conversations to be judged: {len(conversations_filtered)}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for conv in conversations_filtered:
            future = executor.submit(task, conv, fn_llmscored_raw)
            futures.append(future)
        print(f"Executing {len(futures)} tasks")
        num_errors = 0
        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
            r = future.result()  # 获取结果以捕获异常并打印错误信息
            if r: num_errors += 1
        print(f"# of errors: {num_errors}")

with open(fn_conversations, "rb") as f:
    conversations = pickle.load(f)
# TODO: LLM 错误 -- 规范化输出? 
llm_eval(conversations)

# %%
# 压缩, 方便加载
df = pd.read_json(fn_llmscored_raw, lines=True)
df.sort_values(["workflow_name", "workflow_id"], inplace=True)
df_gpt = df[["workflow_name", "workflow_id", "judge_result"]]
df_gpt.to_json(fn_llmscored, orient="records", lines=True, force_ascii=False)



# %%
# ===================================================================================
#                convert to format of doc -- 方便和人工标注结果进行比较
# https://doc.weixin.qq.com/sheet/e3_Aa8AFwbhAEsNvUX5XUlTXSTGWsT5A?scode=AJEAIQdfAAok83fN9fAcMATAZtAPI&tab=d88els

converted = []
# TODO: errors is List instead of Dict??
# cols: [score, error_types]
for idx, row in df.iterrows():
    id_ = f"{row['workflow_name']}_{row['workflow_id']:03d}"
    jr = row["judge_result"]
    converted.append((id_, jr["overall"]["score"], None))
    converted.append((None, None, None))
    for round_id, round_eval in sorted(jr["detailed"].items(), key=lambda x: x[0]):
        errors = round_eval["errors"]
        error_types_str = ",".join(errors.keys() if errors else [])
        converted.append((round_id, None, None))
        converted.append((str(errors), round_eval["score"], error_types_str))
len(converted)
# %%
df_converted = pd.DataFrame(converted, columns=["misc", "score", "error_types"])

from easonsi.files.gsheet import GSheet
gsheet = GSheet()
gsheet.to_gsheet(df_converted, sheet_name="llm_eval_results")

# %%
