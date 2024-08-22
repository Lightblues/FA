

# %%
import os, json, tqdm, itertools, pickle
import pandas as pd
import concurrent.futures
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
def task(conv, ofn):
    workflow_name = conv["workflow_name"]
    pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu_step3 / f"{workflow_name}.yaml")
    s_conv = tabulate(conv["simulated_conversation"], headers="keys", showindex=False, tablefmt='psql', maxcolwidths=100)
    prompt = jinja_render(
        "scorer_detailed.jinja",
        conversation=s_conv,
        PDL=pdl.to_str(),
    )
    res = client.query_one(prompt)
    res_formatted = Formater.parse_llm_output_yaml(res)
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
    return out

def llm_eval(conversations, max_workers=20):
    ofn = _ddir / "conversations_eval.jsonl"
    skipped = set()
    if os.path.exists(ofn):
        existed = utils.LoadJsonl(ofn)
        for d in existed:
            skipped.add((
                d["workflow_name"], d["workflow_id"]
            ))
    conversations_filtered = [c for c in conversations if (c["workflow_name"], c["workflow_id"]) not in skipped]
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for conv in conversations_filtered:
            future = executor.submit(task, conv, ofn)
        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
            future.result()  # 获取结果以捕获异常并打印错误信息

llm_eval(conversations)
# %%
