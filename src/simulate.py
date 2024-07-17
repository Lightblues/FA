""" 
python simulate.py --workflow_dir huabu_refine01 --workflow_name 000 --ref_conversation_id 0
"""

import os, argparse, json
from simulator.simulator import Simulator
from engine_v1.datamodel import Conversation
from engine_v1.common import DIR_conversation, DIR_data, DataManager, LLM_CFG, init_client

workflow_id_map = DataManager.build_workflow_id_map(DIR_conversation, extension=".json")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="qwen2_72B", choices=list(LLM_CFG.keys()))
    parser.add_argument("--workflow_dir", type=str, default="huabu_refine01")       # huabu_v3, manual
    parser.add_argument("--workflow_name", type=str, default="000")
    parser.add_argument("--ref_conversation_id", type=int, default=0)
    args = parser.parse_args()
    return args

def load_ref_conversation(workflow_name:str, ref_conversation_id:int):
    try:
        workflow_name = workflow_id_map[workflow_name]
    except KeyError:
        raise ValueError(f"Unknown workflow_name: {workflow_name}! Please choose from {workflow_id_map}")
    fn = f"{DIR_conversation}/{workflow_name}.json"
    with open(fn, "r") as f:
        ref_conversation_json = json.load(f)[ref_conversation_id]
    ref_conversation = Conversation.load_from_json(ref_conversation_json)
    return ref_conversation

if __name__ == '__main__':
    args = get_args()
    workflow_dir:str = args.workflow_dir
    if not workflow_dir.startswith("/apdcephfs"):
        workflow_dir = f"/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu/data/v240628/{workflow_dir}"
    client = init_client(llm_cfg=LLM_CFG[args.model_name])
    simulator = Simulator(client=client, workflow_dir=workflow_dir)
    ref_conversation = load_ref_conversation(args.workflow_name, args.ref_conversation_id)
    _ = simulator.simulate(workflow_name=args.workflow_name, ref_conversation=ref_conversation)