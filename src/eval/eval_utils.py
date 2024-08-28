import os, json, tqdm, itertools, pickle, collections, traceback, datetime, tabulate
from typing import List, Dict, Optional, Tuple
import pandas as pd
import concurrent.futures
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL, Config, UserProfile
from simulator import SimulatorV2
from utils.jinja_templates import jinja_render


# 转为便于表格展示的两个形式的数据
# 对于每一组对话, 第一行为meta信息, 第二行为bot  greeting, 后面的 U/B 之间的会话
def parse_conv(conversation_s:str):
    convs: list[str] = []   # [user1, bot1, user2, bot2, ...]
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


# 转为规范的数据格式, {workflow_name, workflow_id, user_profile, simulated_conversation}
def convert_conv(df:pd.DataFrame):
    conversations = []
    
    df.columns = ["round", "content"]
    mask = df["round"].str.startswith('0')
    idx = list(df[mask].index)  + [len(df)]
    for s,e in itertools.pairwise(idx):
        id_, user_profile = df.iloc[s,0], df.iloc[s,1]
        workflow_name, workflow_id = id_.split("_", 1)
        # print(workflow_name, workflow_id)
        conv = df.iloc[s+1:e, :].values.tolist()
        # print(conv)
        conversations.append({
            "workflow_name": workflow_name,
            "workflow_id": int(workflow_id),
            "user_profile": user_profile,
            "simulated_conversation": conv,
        })
    return conversations


def task_simulate(cfg: Config, user_profile_json: Dict, workflow_name, ofn) -> None:
    """ One simulation task
    TODO: add retry & raise!
    """
    fp = open(ofn, "a+", encoding="utf-8")
    user_profile = UserProfile.load_from_dict(user_profile_json)
    
    simulator = SimulatorV2(cfg)
    infos, conversation = simulator.start_simulation(user_profile)
    simulated_res = {
        "workflow_name": workflow_name,
        "simulated_conversation": conversation.to_str(),
        "user_profile": user_profile.to_str(),
        "meta_infos": infos,
    }
    fp.write(json.dumps(simulated_res, ensure_ascii=False)+"\n")
    fp.flush()
    fp.close()

def valid_judge_result(jr: Dict):
    assert "overall" in jr and "detailed" in jr, f"Invalid judge result: {jr}"
    assert "score" in jr["overall"] and isinstance(jr["overall"]["score"], (int, float)), f"Invalid judge result: {jr}"
    for _, round_eval in jr["detailed"].items():
        assert "score" in round_eval and isinstance(round_eval["score"], (int, float)), f"Invalid judge result: {jr}"
        errors = round_eval["errors"]
        if errors:
            assert isinstance(errors, dict), f"Invalid judge result: {jr}"
        

def task_judge(conv, ofn, client: OpenAIClient) -> None:
    workflow_name = conv["workflow_name"]
    pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu_step3 / f"{workflow_name}.yaml")
    s_conv = tabulate.tabulate(conv["simulated_conversation"], headers="keys", showindex=False, maxcolwidths=100) # , tablefmt='psql'
    prompt = jinja_render(
        "scorer_detailed.jinja",
        conversation=s_conv,
        PDL=pdl.to_str(),
    )
    for retry_ in range(3):
        try:
            res = client.query_one(prompt)
            jr = Formater.parse_llm_output_yaml(res)
            if "error" in jr:
                continue
            # TODO: check the format of res
            valid_judge_result(jr)
            out = {
                "workflow_name": workflow_name,
                "workflow_id": conv["workflow_id"],
                "judge_result": jr,
                "infos": {
                    "prompt": prompt,
                    "response": res,
                    "user_profile": conv["user_profile"]
                }
            }
            with open(ofn, "a") as f:
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
            break
        except Exception as e:
            continue
    else:
        traceback.print_exc()
        raise Exception(f"Judge failed 3 times for {workflow_name}")

# %%
from easonsi import utils
import traceback
def remove_dup_lines(fn):
    # for judge_result
    data = utils.LoadJsonl(fn)
    data_filtered = []
    exist = set()
    for d in data:
        key = (d['workflow_name'], d["workflow_id"])
        if key not in exist:
            data_filtered.append(d)
            exist.add(key)
    utils.SaveJsonl(data_filtered, fn)
# remove_dup_lines("/work/huabu/data/v240820/simulated/v240828/eval_gpt_detailed.jsonl")
def remove_unvalid_judge_result(fn):
    data = utils.LoadJsonl(fn)
    data_filtered = []
    cnt_removed = 0
    for d in data:
        try:
            valid_judge_result(d["judge_result"])
            data_filtered.append(d)
        except:
            print(f"Invalid judge result: {d['workflow_name']}, {d['workflow_id']}")
            traceback.print_exc()
            cnt_removed += 1
    if cnt_removed < 5:
        utils.SaveJsonl(data_filtered, fn)
# remove_unvalid_judge_result("/work/huabu/data/v240820/simulated/v240828_02/eval_gpt_detailed.jsonl")
# %%
