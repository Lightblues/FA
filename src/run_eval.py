""" 
USAGE: 
    python run_eval.py --workflow_dir=pdl_v0828 --model=v0729-Llama3_1-70B --version=v240828_01
    python run_eval.py --workflow_dir=pdl_v0828 --model=Qwen2-72B --version=v240828_02
    python run_eval.py --workflow_dir=pdl_v0828 --model=v0729-Qwen2-7B --version=v240828_03
    
"""

import os, argparse, json
from eval.evaluator import Evaluator
from engine import Conversation, _DIRECTORY_MANAGER, DataManager, LLM_CFG, init_client, UserProfile, Config, PDL

workflow_id_map = DataManager.build_workflow_id_map(_DIRECTORY_MANAGER.DIR_huabu_step3, extension=".yaml")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="simulate.yaml")
    parser.add_argument("--version", type=str, default=None)
    parser.add_argument("--model_name", type=str, default=None, choices=list(LLM_CFG.keys())) # "qwen2_72B"
    parser.add_argument("--workflow_dir", type=str, default=None)       # pdl_v0828
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    cfg = Config.from_yaml(DataManager.normalize_config_name(args.config))
    if args.version: cfg.simulate_version = args.version
    if args.model_name: cfg.simulate_model_name = args.model_name
    if args.workflow_dir: cfg.workflow_dir = args.workflow_dir
    evaluator = Evaluator(cfg)
    evaluator.main()