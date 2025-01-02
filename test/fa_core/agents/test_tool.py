from fa_core.common import Config
from fa_core.data import APIOutput, BotOutput, Conversation, FAWorkflow
from fa_core.agents import RequestTool, Context


def test_request_tool_llm():
    """
    @241223:
    - 测试医院名称归一化
    """
    cfg = Config.from_yaml("dev.yaml")
    cfg.workflow_dataset = "pdl_converted_20241223_hyturbo"
    cfg.workflow_id = "006"  # GuaHao, with LLM nodes
    conv = Conversation()
    data_handler = FAWorkflow.from_config(cfg)
    context = Context(cfg=cfg, conv=conv, workflow=data_handler)
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
    data_handler = FAWorkflow.from_config(cfg)
    context = Context(cfg=cfg, conv=conv, workflow=data_handler)
    tool = RequestTool(cfg=cfg, context=context)

    bot_output = BotOutput(
        thought="...",
        action="获取挂号时间和号类",
        action_input={"data": [{"num_type": "普通号", "time": "3月22日"}], "num": 1},
        response=None,
    )
    api_output: APIOutput = tool.process(bot_output)
    print(api_output)


def test_request_tool_post_000():
    cfg = Config.from_yaml("dev.yaml")
    cfg.workflow_dataset = "v241127_converted_ruled"
    cfg.workflow_id = "000"
    conv = Conversation()
    data_handler = FAWorkflow.from_config(cfg)
    context = Context(cfg=cfg, conv=conv, workflow=data_handler)
    tool = RequestTool(cfg=cfg, context=context)

    for bot_output in [
        BotOutput(action="销售信息查询", action_input={"account": "S1722sw12024"}),
        BotOutput(action="检查发件邮编城市", action_input={"postalCode": "100000", "city": "北京"}),
        BotOutput(action="检查国家或地区是否有邮编", action_input={"countryCode": "CN"}),
        BotOutput(action="检查收件邮编城市", action_input={"postalCode": "100000", "city": "北京"}),
        BotOutput(action="检查收件城市", action_input={"city": "北京", "countryCode": "CN"}),
        BotOutput(
            action="运费时效包裹类",
            action_input={
                "fromCountryCode": "CN",
                "fromPostalCode": "100000",
                "toCountryCode": "CN",
                "toPostalCode": "100000",
                "productType": "文件",
                "declaredValue": 100,
                "goodsWeight": 1,
                "goodsLength": 1,
                "goodsWidth": 1,
                "goodsHeight": 1,
                "goodsName": "文件",
                "sendTime": "2025-01-01",
            },
        ),
        BotOutput(
            action="运费时效文件类",
            action_input={
                "fromCountryCode": "CN",
                "fromPostalCode": "100000",
                "toCountryCode": "CN",
                "toPostalCode": "100000",
                "productType": "文件",
                "declaredValue": 100,
                "goodsWeight": 1,
                "goodsLength": 1,
                "goodsWidth": 1,
                "goodsHeight": 1,
                "goodsName": "文件",
                "sendTime": "2025-01-01",
            },
        ),
    ]:
        api_output: APIOutput = tool.process(bot_output)
        print(api_output)


def test_request_tool_post_007():
    cfg = Config.from_yaml("dev.yaml")
    cfg.workflow_dataset = "v241127_converted_llm"
    cfg.workflow_id = "007"
    conv = Conversation()
    data_handler = FAWorkflow.from_config(cfg)
    context = Context(cfg=cfg, conv=conv, workflow=data_handler)
    tool = RequestTool(cfg=cfg, context=context)

    for bot_output in [
        BotOutput(action="查验目的地清关政策", action_input={"countryCode": "DE"}),
        BotOutput(action="物品目的地清关提示", action_input={"countryCode": "DE", "goodsName": "手机"}),
        BotOutput(action="物品目的地清关提示", action_input={"countryCode": "CN", "goodsName": "玻璃制品"}),
    ]:
        api_output: APIOutput = tool.process(bot_output)
        print(api_output)


# test_request_tool_llm()
# test_request_tool_code_executor()
test_request_tool_post_007()
