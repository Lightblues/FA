""" 
python run_cli.py --config=default.yaml --workflow_dir=pdl2_step3 --workflow_name=000
python run_cli.py --config=test.yaml --workflow_dir=pdl2_step3 --workflow_name=000
"""

import os, argparse
from engine import (
    LLM_CFG, DataManager, ConversationController, Config
)

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="default.yaml")
    # -- overwrite config --
    parser.add_argument("--model_name", type=str, default=None, choices=list(LLM_CFG.keys()))
    parser.add_argument("--template_fn", type=str, default=None)          # "query_PDL.jinja"
    parser.add_argument("--workflow_dir", type=str, default=None)         # huabu_v3, huabu_manual, huabu_refine01
    parser.add_argument("--workflow_name", type=str, default=None)
    parser.add_argument("--api_mode", type=str, default=None, choices=["manual", "llm", "v01"])
    parser.add_argument("--check_dependency", type=bool, default=None, help="whether or not to check dependency between nodes.")
    parser.add_argument("--check_duplicate", type=bool, default=None, help="whether or not to do duplication check for API call.")
    parser.add_argument("--max_duplicated_limit", type=int, default=None, help="The maximum count limit for a certain api to be called continously")
    parser.add_argument("--api_entity_linking", type=bool, default=None)
    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()

    cfg = Config.from_yaml(
        DataManager.normalize_config_name(args.config),
    )
    if args.model_name: cfg.model_name = args.model_name
    if args.template_fn: cfg.template_fn = args.template_fn
    if args.workflow_dir: cfg.workflow_dir = args.workflow_dir
    if args.workflow_name: cfg.workflow_name = args.workflow_name
    if args.api_mode is not None: cfg.api_mode = args.api_mode
    if args.check_dependency is not None: cfg.check_dependency = args.check_dependency
    if args.check_duplicate is not None: cfg.check_duplicate = args.check_duplicate
    if args.max_duplicated_limit is not None: cfg.max_duplicated_limit = args.max_duplicated_limit
    if args.api_entity_linking is not None: cfg.api_entity_linking = args.api_entity_linking
    cfg.workflow_dir = DataManager.normalize_workflow_dir(cfg.workflow_dir)
    cfg.workflow_name = DataManager.normalize_workflow_name(cfg.workflow_name, cfg.workflow_dir, cfg.pdl_extension)
    # print(f">> config: {cfg}")
    
    controller = ConversationController(cfg)
    controller.start_conversation()
