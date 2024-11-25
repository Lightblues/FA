from flowagent import Config, DataManager
from flowagent.data import Conversation, Workflow, BotOutput, APIOutput
from flowagent.roles import LLMSimulatedTool, RequestTool

def init_llm_api() -> LLMSimulatedTool:
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    conv = Conversation()
    pdl = Workflow(cfg)
    tool = LLMSimulatedTool(cfg=cfg, conv=conv, workflow=pdl)
    return tool

def init_request_api() -> RequestTool:
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.workflow_dataset = "PDL_zh"
    cfg.workflow_id = "000"
    conv = Conversation()
    pdl = Workflow(cfg)
    tool = RequestTool(cfg=cfg, conv=conv, workflow=pdl)
    return tool

# tool = init_llm_api()
tool = init_request_api()

# bot_output = BotOutput(thought="...", action="check_hospital", action_input={"test": "test"}, response=None)
bot_output = BotOutput(thought="...", action="check_hospital", action_input={"hospital_name": "test"}, response=None)
api_output: APIOutput = tool.process(bot_output)
print(api_output)
print()
