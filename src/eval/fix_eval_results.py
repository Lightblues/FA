""" 
fix some formating errors, tmp file!
"""


# %%
import traceback, tqdm
from easonsi import utils
from eval.eval_utils import valid_judge_result

def remove_dup_lines(fn):
    # remove duplicated lines
    data = utils.LoadJsonl(fn)
    data_filtered = []
    exist = set()
    for d in data:
        key = (d['workflow_name'], d["workflow_id"])
        if key not in exist:
            data_filtered.append(d)
            exist.add(key)
    utils.SaveJsonl(data_filtered, fn)

def remove_unvalid_judge_result(fn, fn2):
    # remove unvalid judge results
    data = utils.LoadJsonl(fn)
    data.sort(key=lambda x: (x["workflow_name"], x["workflow_id"]))
    conversations = utils.LoadJsonl(fn2)
    conversations.sort(key=lambda x: (x["workflow_name"], x["workflow_id"]))
    data_filtered = []
    cnt_removed = 0
    assert len(data) == len(conversations)
    for d,c in tqdm.tqdm(zip(data, conversations)):
        try:
            valid_judge_result(d["judge_result"], num_rounds=len(c["simulated_conversation"]) // 2)
            data_filtered.append(d)
        except:
            print(f"Invalid judge result: {d['workflow_name']}, {d['workflow_id']}")
            traceback.print_exc()
            cnt_removed += 1
    print(f"Removed {cnt_removed} invalid results")
    if cnt_removed <= 5:    # duble check before deleting!
        utils.SaveJsonl(data_filtered, fn)


# remove_dup_lines("/work/huabu/data/v240820/simulated/v240828/eval_gpt_detailed.jsonl")
_dir = "/work/huabu/data/v240820/simulated/v240828_01"
_dir = "/work/huabu/data/v240820/simulated/v240828_02"
remove_unvalid_judge_result(
    f"{_dir}/eval_gpt_detailed.jsonl",
    f"{_dir}/simulated_conversations.jsonl")

# %%
