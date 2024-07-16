""" 
@240716 并发模拟此前的 conversation, 保存到 $DATA/simulated 下
"""
import os, argparse, json
from tqdm import tqdm
import concurrent.futures
from simulator.simulator import Simulator
from engine_v1.datamodel import Conversation
from engine_v1.common import DIR_conversation, DIR_data, DIR_simulated, DataManager, LLM_CFG, init_client

workflow_id_map = DataManager.build_workflow_id_map(DIR_conversation, extension=".json")

def load_ref_conversation(workflow_name:str, ref_conversation_id:int):
    workflow_name = workflow_id_map[workflow_name]
    fn = f"{DIR_conversation}/{workflow_name}.json"
    with open(fn, "r") as f:
        ref_conversation_json = json.load(f)[ref_conversation_id]
    ref_conversation = Conversation.load_from_json(ref_conversation_json)
    return ref_conversation


def run_single_simulate(workflow_name):
    ofn = f"{DIR_simulated}/{workflow_name}.json"
    if os.path.exists(ofn):
        print(f"[warning] {ofn} exists, skip")
        return
    data = []
    fn = f"{DIR_conversation}/{workflow_name}.json"
    with open(fn, "r") as f:
        ref_conversation_jsons = json.load(f)
    for ref_conversation_id, ref_conversation_json in enumerate(ref_conversation_jsons):
        ref_conversation = Conversation.load_from_json(ref_conversation_json)
        infos, conversation = simulator.simulate(workflow_name, ref_conversation)
        data.append({
            "workflow_name": workflow_name,
            "ref_conversation": ref_conversation.to_str(),
            "simulated_conversation": conversation.to_str(),
            "meta_infos": infos,
        })
    with open(ofn, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Saved to {ofn}")
    return data


model_name = "qwen2_72B"
client = init_client(llm_cfg=LLM_CFG[model_name])
simulator = Simulator(client=client, workflow_dir=DIR_data)

max_workers = 10
workflow_names = DataManager.get_workflow_name_list(DIR_conversation, extension=".json")
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []
    for workflow_name in workflow_names:
        future = executor.submit(run_single_simulate, workflow_name)
        futures.append(future)
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        try:
            res_ = future.result()
        except Exception as e:
            print(f"[ERROR] for future: {future}\n{e}")
            for f in futures:
                f.cancel()
            raise e