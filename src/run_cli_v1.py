""" 
python run_cli_v1.py --workflow_dir huabu_refine01 --workflow_name 000
"""

import os, argparse
from engine_v1.interface import CLIInterface
from engine_v1.common import init_client, LLM_CFG

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="qwen2_72B", choices=list(LLM_CFG.keys()))    # SN, gpt-4o
    parser.add_argument("--workflow_dir", type=str, default="huabu_refine01")       # huabu_v3, manual
    parser.add_argument("--workflow_name", type=str, default="000")
    parser.add_argument("--api_mode", type=str, default="manual", choices=["manual", "llm", "vanilla"])
    parser.add_argument("--template_fn", type=str, default="query_PDL.jinja")
    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    client = init_client(llm_cfg=LLM_CFG[args.model_name])
    workflow_dir:str = args.workflow_dir
    if not workflow_dir.startswith("/apdcephfs"):
        workflow_dir = f"/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu/data/v240628/{workflow_dir}"
    interface = CLIInterface(client=client, api_mode=args.api_mode, workflow_dir=workflow_dir, template_fn=args.template_fn)
    interface.conversation(workflow_name=args.workflow_name)
