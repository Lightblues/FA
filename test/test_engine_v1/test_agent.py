from engine_v1.agent import Agent
from engine_v1.common import init_client
from main import LLM_CFG
# change workdir to ..
import os; os.chdir("../../src")

client = init_client(llm_cfg=LLM_CFG["SN"])
# client = init_client(llm_cfg=LLM_CFG["gpt-4o"])
agent = Agent(client=client)
agent.conversation(workflow_name="011-银行订单查询")
