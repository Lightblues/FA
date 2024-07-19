""" 
python run_cli_v2.py --workflow_dir huabu_refine01 --workflow_name 000
"""

import os, argparse
from engine_v1.interface import CLIInterface
from engine_v1.common import init_client, LLM_CFG, DataManager
from engine_v2.main import ConversationController
from engine_v2.datamodel import Config

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="default.yaml")
    # -- overwrite config --
    parser.add_argument("--model_name", type=str, default=None, choices=list(LLM_CFG.keys()))
    parser.add_argument("--workflow_dir", type=str, default=None)         # huabu_v3, manual, huabu_refine01
    parser.add_argument("--workflow_name", type=str, default=None)
    parser.add_argument("--template_fn", type=str, default=None)          # "query_PDL.jinja"
    # parser.add_argument("--api_mode", type=str, default="manual", choices=["manual", "llm", "vanilla"])
    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()

    cfg = Config.from_yaml(
        DataManager.normalize_config_name(args.config),
    )
    if args.model_name: cfg.model_name = args.model_name
    if args.workflow_dir: cfg.workflow_dir = args.workflow_dir
    if args.workflow_name: cfg.workflow_name = args.workflow_name
    if args.template_fn: cfg.template_fn = args.template_fn
    cfg.workflow_dir = DataManager.normalize_workflow_dir(cfg.workflow_dir)
    cfg.workflow_name = DataManager.normalize_workflow_name(cfg.workflow_name, cfg.workflow_dir)
    print(f"config: {cfg}")
    
    controller = ConversationController(cfg)
    controller.start_conversation()
