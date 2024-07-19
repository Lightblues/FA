from engine_v1.interface import CLIInterface
from engine_v1.common import init_client
from run_cli_v1 import LLM_CFG
# change workdir to ..
import os; os.chdir("../../src")

client = init_client(llm_cfg=LLM_CFG["SN"])
# client = init_client(llm_cfg=LLM_CFG["gpt-4o"])
agent = CLIInterface(client=client)
agent.conversation(workflow_name="011-银行订单查询")
