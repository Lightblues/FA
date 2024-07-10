import os, argparse
# os.environ["PYTHONPATH"] = f"{os.getcwd()}:/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/easonsi/src/"
# print("PYTHONPATH=", os.getenv("PYTHONPATH"))
from engine_v1.agent import Agent
from engine_v1.common import init_client, LLM_CFG

def get_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--model_name", type=str, default="SN")
    # parser.add_argument("--model_name", type=str, default="gpt-4o")
    parser.add_argument("--model_name", type=str, default="qwen2_72B", choices=list(LLM_CFG.keys()))
    # parser.add_argument("--workflow_name", type=str, default="011-银行订单查询")
    parser.add_argument("--workflow_name", type=str, default="022-挂号")
    parser.add_argument("--api_mode", type=str, default="manual", choices=["manual", "llm", "vanilla"])
    
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    client = init_client(llm_cfg=LLM_CFG[args.model_name])
    agent = Agent(client=client, api_mode=args.api_mode)
    agent.conversation(workflow_name=args.workflow_name)