""" 
USAGE: 
    python run_simulate.py --workflow_dir=pdl --workflow_name=000
"""

import os, argparse, json
from simulator.simulator_with_profile import SimulatorV2
from engine import Conversation, _DIRECTORY_MANAGER, DataManager, LLM_CFG, init_client, UserProfile, Config, PDL

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="simulate.yaml")
    parser.add_argument("--model_name", type=str, default="qwen2_72B", choices=list(LLM_CFG.keys()))
    parser.add_argument("--workflow_dir", type=str, default=None)       # pdl, manual
    parser.add_argument("--workflow_name", type=str, default=None)
    parser.add_argument("--profile_id", type=int, default=0)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    cfg = Config.from_yaml(DataManager.normalize_config_name(args.config))
    if args.workflow_dir: cfg.workflow_dir = args.workflow_dir
    if args.workflow_name: cfg.workflow_name = args.workflow_name
    if args.model_name: cfg.model_name = args.model_name
    
    fn = _DIRECTORY_MANAGER.DIR_user_profile / f"{cfg.workflow_name}.json"
    with open(fn, "r") as f:
        user_profile_jsons = json.load(f)
    profile = UserProfile.load_from_dict(user_profile_jsons[args.profile_id])
    simulator = SimulatorV2(cfg)
    _ = simulator.start_simulation(profile=profile)
