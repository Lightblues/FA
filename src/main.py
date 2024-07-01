import os, argparse
# os.environ["PYTHONPATH"] = f"{os.getcwd()}:/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/easonsi/src/"
# print("PYTHONPATH=", os.getenv("PYTHONPATH"))
from engine_v1.agent import Agent
from engine_v1.common import init_client

# llm_cfg = {
#     # "base_url": os.getenv("OPENAI_WIZARD_BASE_URL"),
#     # "api_key": os.getenv("OPENAI_WIZARD_API_KEY"),
#     "base_url": os.getenv("OPENAI_QWEN2_BASE_URL"),
#     "api_key": os.getenv("OPENAI_QWEN2_API_KEY"),
#     # "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
#     # "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
#     "model_name": "gpt-4o"
# }
LLM_CFG = {
    "SN": {
        "model_name": "神农大模型",
        "base_url": "http://9.91.12.52:8001",
        "api_key": "xxx",
    },
    "gpt-4o": {
        "model_name": "gpt-4o",
        "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
        "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
    }
}

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="SN")
    parser.add_argument("--workflow_name", type=str, default="011-银行订单查询")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    client = init_client(llm_cfg=LLM_CFG[args.model_name])
    agent = Agent(client=client)
    agent.conversation(workflow_name=args.workflow_name)