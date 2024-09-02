""" 
python run_simulate_siqi.py --workflow_dir pdl2_step3 --workflow_name 000
"""

import os, argparse, json
from simulator.simulator_with_profile import SimulatorV2
from engine import Conversation, _DIRECTORY_MANAGER, DataManager, LLM_CFG, init_client, UserProfile, Config, PDL

workflow_id_map = DataManager.build_workflow_id_map(_DIRECTORY_MANAGER.DIR_huabu, extension=".yaml")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="qwen2_72B", choices=list(LLM_CFG.keys()))
    parser.add_argument("--workflow_dir", type=str, default="huabu_refine01")       # huabu_v3, manual
    parser.add_argument("--workflow_name", type=str, default="000")
    parser.add_argument("--profile_id", type=int, default=0)
    args = parser.parse_args()
    return args

def load_profile(workflow_name:str, profile_id:int):
    try:
        workflow_name = workflow_id_map[workflow_name]
    except KeyError:
        raise ValueError(f"Unknown workflow_name: {workflow_name}! Please choose from {workflow_id_map.keys()}")
    DIR_PROFILE = '/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu/data/gen/user_profile'
    fn = f"{DIR_PROFILE}/{workflow_name}.json"
    with open(fn, "r") as f:
        profile_json = json.load(f)[profile_id]
    profile = UserProfile.load_from_dict(profile_json)
    return profile

if __name__ == '__main__':
    args = get_args()
    workflow_dir:str = args.workflow_dir
    if not workflow_dir.startswith("/apdcephfs"):
        workflow_dir = f"/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu/data/v240820/{workflow_dir}"
    cfg = Config.from_yaml("/work/huabu/src/configs/simulate.yaml")
    simulator = SimulatorV2(cfg)
    profile = load_profile(args.workflow_name, args.profile_id)
    # pdl = PDL.load_from_file(f"{workflow_dir}/{workflow_id_map[args.workflow_name]}.yaml")
    _ = simulator.start_simulation(profile=profile)
