""" updated 240906
usage:
    python run_baseline.py --config=default.yaml \
        --workflow_type=text --workflow_id=000 \
        --user_template_fn=baselines/user_llm.jinja --bot_template_fn=baselines/flowbench.jinja \
        --conversation_turn_limit=20 --log_utterence_time=True
"""

import os, argparse
from baselines import Config, BaselineController, DataManager

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="default.yaml")
    # -- overwrite config --
    parser.add_argument("--workflow_type", type=str, default=None)
    parser.add_argument("--workflow_id", type=str, default=None)
    parser.add_argument("--user_mode", type=str, default=None)
    parser.add_argument("--user_template_fn", type=str, default=None)
    parser.add_argument("--bot_template_fn", type=str, default=None)
    # parser.add_argument("--model_name", type=str, default=None, choices=list(LLM_CFG.keys()))
    # parser.add_argument("--api_mode", type=str, default=None, choices=["manual", "llm", "v01"])
    parser.add_argument("--conversation_turn_limit", type=int, default=None)
    parser.add_argument("--log_utterence_time", type=bool, default=None)
    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()

    data_manager = DataManager()
    cfg = Config.from_yaml(data_manager.normalize_config_name(args.config))
    if args.workflow_type is not None: cfg.workflow_type = args.workflow_type
    if args.workflow_id is not None: cfg.workflow_id = args.workflow_id
    if args.user_mode is not None: cfg.user_mode = args.user_mode
    if args.user_template_fn is not None: cfg.user_template_fn = args.user_template_fn
    if args.bot_template_fn is not None: cfg.bot_template_fn = args.bot_template_fn
    if args.conversation_turn_limit is not None: cfg.conversation_turn_limit = args.conversation_turn_limit
    if args.log_utterence_time is not None: cfg.log_utterence_time = args.log_utterence_time
    # print(f">> config: {cfg}")
    
    controller = BaselineController(cfg)
    controller.start_conversation()
