from common import Config
from flowagent.data import APIOutput, BotOutput, Conversation, DataHandler
from flowagent.roles import LLMSimulatedTool, RequestTool


def init_llm_api() -> LLMSimulatedTool:
    cfg = Config.from_yaml("default.yaml")
    conv = Conversation()
    pdl = DataHandler.create(cfg)
    tool = LLMSimulatedTool(cfg=cfg, conv=conv, workflow=pdl)
    return tool


def init_request_api() -> RequestTool:
    cfg = Config.from_yaml("ui_dev.yaml")
    # cfg.workflow_dataset = "PDL_zh"
    cfg.workflow_dataset = "v241127"
    cfg.workflow_id = "000"
    conv = Conversation()
    pdl = DataHandler.create(cfg)
    tool = RequestTool(cfg=cfg, conv=conv, workflow=pdl)
    return tool


# tool = init_llm_api()
tool = init_request_api()

# bot_output = BotOutput(thought="...", action="check_hospital_exist", action_input={"test": "test"}, response=None)
bot_output = BotOutput(
    thought="...",
    action="check_hospital_exist",
    action_input={"hos_name": "301"},
    response=None,
)
api_output: APIOutput = tool.process(bot_output)
print(api_output)
print(tool.conv)
print()
