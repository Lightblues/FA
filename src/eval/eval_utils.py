import os, json, tqdm, itertools, pickle, collections, traceback, datetime, tabulate
from typing import List, Dict, Optional, Tuple
import pandas as pd
import concurrent.futures
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL, Config, UserProfile
from simulator import Simulator
from utils.jinja_templates import jinja_render

# 转为便于表格展示的两个形式的数据
# 对于每一组对话, 第一行为meta信息, 第二行为bot  greeting, 后面的 U/B 之间的会话
def parse_conv(conversation_s:str):
    convs: list[str] = []   # [user1, bot1, user2, bot2, ...]
    role, utterence = None, ""
    for line in conversation_s.split("\n"):
        if not line.strip(): continue
        if line.startswith("[BOT]"):
            if role!='bot':
                if utterence: convs.append(utterence)
                utterence = line
            else: utterence += f"\n{line}"
            role = "bot"
        elif line.startswith("[USER]"):
            if role!='user': 
                if utterence: convs.append(utterence)
                utterence = line
            else: utterence += f"\n{line}"
            role = "user"
        else:
            if utterence: utterence += f"\n{line}"
    convs.append(utterence)
    if len(convs) % 2 != 1: # Make sure that the bot finish the last user query
        print(f"WARNING! conversation not end with bot! \n{convs}")
    return convs

# 转为规范的数据格式, {workflow_name, workflow_id, user_profile, simulated_conversation}
def convert_conv(df:pd.DataFrame):
    conversations = []
    
    df.columns = ["turn", "content"]
    mask = df["turn"].str.startswith('0')
    idx = list(df[mask].index)  + [len(df)]
    for s,e in itertools.pairwise(idx):
        id_, user_profile = df.iloc[s,0], df.iloc[s,1]
        workflow_name, workflow_id = id_.split("_", 1)
        conv = df.iloc[s+1:e, :].values.tolist()
        assert len(conv) % 2 == 1, f"Invalid conversation: {conv}"
        conversations.append({
            "workflow_name": workflow_name,
            "workflow_id": int(workflow_id),
            "user_profile": user_profile,
            "simulated_conversation": conv,
        })
    return conversations


def task_simulate(cfg: Config, user_profile_json: Dict, workflow_name, ofn) -> None:
    """ One simulation task
    [x] add retry & raise? -- DONE in `Evaluator.run_simulations()`
    """
    fp = open(ofn, "a+", encoding="utf-8")
    user_profile = UserProfile.load_from_dict(user_profile_json)
    
    simulator = Simulator(cfg)
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

def valid_judge_result(jr: Dict, num_turns: int):
    assert "overall" in jr and "detailed" in jr, f"Invalid judge result: {jr}"
    assert "score" in jr["overall"] and isinstance(jr["overall"]["score"], (int, float)), f"Invalid judge result: {jr}"
    assert len(jr["detailed"]) == num_turns, f">> judger generated {len(jr['detailed'])}!={num_turns}\nInvalid judge result: {jr}"
    for _, turn_eval in jr["detailed"].items():
        assert "score" in turn_eval and isinstance(turn_eval["score"], (int, float)), f"Invalid judge result: {jr}"
        errors = turn_eval["errors"]
        if errors:
            assert isinstance(errors, dict), f"Invalid judge result: {jr}"
        

def task_judge(conv, ofn, client: OpenAIClient) -> None:
    workflow_name = conv["workflow_name"]
    num_turns = len(conv["simulated_conversation"]) // 2
    pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu / f"{workflow_name}.yaml")
    s_conv = tabulate.tabulate(conv["simulated_conversation"], headers=["turn", "content"], showindex=False, maxcolwidths=100, tablefmt='psql')
    
    prompt = jinja_render(
        "scorer_detailed.jinja",
        conversation=s_conv, num_turns=num_turns,
        PDL=pdl.to_str(),
    )
    for retry_ in range(3):
        try:
            res, _model_name, _usage = client.query_one(prompt, return_usage=True)
            jr = Formater.parse_llm_output_yaml(res)
            if "error" in jr:
                continue
            # DONE @240828: check the format of res
            valid_judge_result(jr, num_turns)
            out = {
                "workflow_name": workflow_name,
                "workflow_id": conv["workflow_id"],
                "judge_model": _model_name,
                "Judge_usage": _usage,
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
            traceback.print_exc()
            continue
    else:
        print(f"ERROR!!! conv:\n{conv}")
        print(f"prompt: {prompt}")
        raise Exception(f"Judge failed 3 times for {workflow_name}")

def task_judge_2(conv, ofn, client: OpenAIClient) -> None:
    workflow_name = conv["workflow_name"]
    num_turns = len(conv["simulated_conversation"]) // 2
    
    pdl = PDL.load_from_file(_DIRECTORY_MANAGER.DIR_huabu / f"{workflow_name}.yaml")
    s_pdl = str(
        dict(
            taskflow_name=pdl.taskflow_name,
            taskflow_desc=pdl.taskflow_desc,
            taskflow_desc_detail=pdl.taskflow_desc_detail,
        )
    )
    def process_utterance(s:str, key:str="[BOT]"):
        if key in s:
            return key + s.split(key)[-1]
        return s
    df_conv = pd.DataFrame(conv["simulated_conversation"], columns=["turn", "content"])
    df_conv["content"] = df_conv["content"].apply(process_utterance)
    s_conv = tabulate.tabulate(df_conv, headers=["turn", "content"], showindex=False, maxcolwidths=100, tablefmt='psql')
    
    prompt = jinja_render(
        "scorer_detailed_2.jinja",
        conversation=s_conv, num_turns=num_turns,
        PDL=s_pdl,
    )
    for retry_ in range(3):
        try:
            res, _model_name, _usage = client.query_one(prompt, return_usage=True)
            jr = Formater.parse_llm_output_yaml(res)
            if "error" in jr:
                continue
            # DONE @240828: check the format of res
            valid_judge_result(jr, num_turns)
            out = {
                "workflow_name": workflow_name,
                "workflow_id": conv["workflow_id"],
                "judge_model": _model_name,
                "Judge_usage": _usage,
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
            traceback.print_exc()
            continue
    else:
        print(f"ERROR!!! conv:\n{conv}")
        print(f"prompt: {prompt}")
        raise Exception(f"Judge failed 3 times for {workflow_name}")

