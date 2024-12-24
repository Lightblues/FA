from fa_core.common import Config
from fa_core.data import APIOutput, BotOutput, Conversation, DataHandler
from fa_core.agents import RequestTool, Context


# def init_llm_api() -> LLMSimulatedTool:
#     cfg = Config.from_yaml("default.yaml")
#     conv = Conversation()
#     pdl = DataHandler.create(cfg)
#     tool = LLMSimulatedTool(cfg=cfg, conv=conv, workflow=pdl)
#     return tool


def test_request_tool_llm():
    """
    @241223:
    - 测试医院名称归一化
    """
    cfg = Config.from_yaml("dev.yaml")
    cfg.workflow_dataset = "pdl_converted_20241223_hyturbo"
    cfg.workflow_id = "006"  # GuaHao, with LLM nodes
    conv = Conversation()
    data_handler = DataHandler.create(cfg)
    context = Context(cfg=cfg, conv=conv, data_handler=data_handler)
    tool = RequestTool(cfg=cfg, context=context)

    bot_output = BotOutput(
        thought="...",
        action="医院名称归一化",
        action_input={"hospital": "301"},
        response=None,
    )
    api_output: APIOutput = tool.process(bot_output)
    print(api_output)


def test_request_tool_code_executor():
    """
    @241223:
    - 测试代码执行器
    """
    cfg = Config.from_yaml("dev.yaml")
    cfg.workflow_dataset = "pdl_converted_20241223_hyturbo"
    cfg.workflow_id = "006"  # GuaHao, with LLM nodes
    conv = Conversation()
    data_handler = DataHandler.create(cfg)
    context = Context(cfg=cfg, conv=conv, data_handler=data_handler)
    tool = RequestTool(cfg=cfg, context=context)

    bot_output = BotOutput(
        thought="...",
        action="获取挂号时间和号类",
        action_input={"data": [{"num_type": "普通号", "time": "3月22日"}], "num": 1},
        response=None,
    )
    api_output: APIOutput = tool.process(bot_output)
    print(api_output)


# bot_output = BotOutput(thought="...", action="check_hospital_exist", action_input={"test": "test"}, response=None)
bot_output = BotOutput(
    thought="...",
    action="check_hospital_exist",
    action_input={"hos_name": "301"},
    response=None,
)

# test_request_tool_llm()
test_request_tool_code_executor()
