""" 
USAGE: 
    python run_eval.py --config=simulate.yaml --workflow_dir=pdl --bot_mode=lke --version=v240830_01
    python run_eval.py --config=simulate.yaml --workflow_dir=pdl --bot_mode=pdl --simulate_model_name=Qwen2-72B --version=v240830_02
    python run_eval.py --config=simulate.yaml --workflow_dir=pdl --bot_mode=pdl --simulate_model_name=0.9.1 --version=v240830_03
    python run_eval.py --config=simulate.yaml --workflow_dir=pdl --bot_mode=pdl --simulate_model_name=v0729-Llama3_1-70B --version=v240830_04
"""

import os, argparse, json
from eval.evaluator import Evaluator
from engine import Conversation, _DIRECTORY_MANAGER, DataManager, LLM_CFG, init_client, UserProfile, Config, PDL, BOT_ANME2CLASS

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="simulate.yaml")
    parser.add_argument("--version", type=str, default=None)
    parser.add_argument("--bot_mode", type=str, default=None, choices=list(BOT_ANME2CLASS.keys()))
    parser.add_argument("--simulate_model_name", type=str, default=None, choices=list(LLM_CFG.keys())) # "qwen2_72B"
    parser.add_argument("--judge_model_name", type=str, default=None, choices=list(LLM_CFG.keys())) # gpt-4o
    parser.add_argument("--judge_passrate_threshold", type=float, default=3)
    parser.add_argument("--workflow_dir", type=str, default=None)       # pdl_v0828
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    cfg = Config.from_yaml(DataManager.normalize_config_name(args.config))
    if args.bot_mode: cfg.bot_mode = args.bot_mode
    if args.version: cfg.simulate_version = args.version
    if args.simulate_model_name: cfg.simulate_model_name = args.simulate_model_name
    if args.workflow_dir: cfg.workflow_dir = args.workflow_dir
    if args.judge_model_name: cfg.judge_model_name = args.judge_model_name
    if args.judge_passrate_threshold: cfg.judge_passrate_threshold = args.judge_passrate_threshold
    evaluator = Evaluator(cfg)
    evaluator.main()