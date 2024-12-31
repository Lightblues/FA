from fa_core.common import Config
from fa_core.data import Conversation, FAWorkflow, Message, Role
from fa_core.agents import Context, UISingleBot, UIMultiMainBot, UIMultiWorkflowBot


def test_ui_single_bot(msg="hello, what can you do?"):
    cfg = Config.from_yaml("default.yaml")
    workflow = FAWorkflow.from_config(cfg)
    conv = Conversation()
    context = Context(cfg=cfg, workflow=workflow, conv=conv)
    bot = UISingleBot(cfg=cfg, context=context)

    conv.add_message(msg=msg, role=Role.USER)
    stream = bot.process_stream()
    for chunk in stream:
        print(chunk, end="")
    print()
    bot_output = bot.process_LLM_response()
    print(bot_output)
    print(conv)
    print()


def test_ui_multi_main_bot(msg="hello, what can you do?"):
    cfg = Config.from_yaml("default.yaml")
    cfg.bot_mode = "multi_main_bot"
    workflow = FAWorkflow.from_config(cfg)
    conv = Conversation()
    context = Context(cfg=cfg, workflow=workflow, conv=conv)
    bot = UIMultiMainBot(cfg=cfg, context=context)
    conv.add_message(msg=msg, role=Role.USER)
    stream = bot.process_stream()
    for chunk in stream:
        print(chunk, end="")
    print()
    bot_output = bot.process_LLM_response()
    print(f"bot_output: {bot_output}")
    print(f"conv: {conv}")
    print()


def test_ui_multi_workflow_bot(msg="挂一个301的号"):
    cfg = Config.from_yaml("default.yaml")
    cfg.bot_mode = "multi_workflow_bot"
    workflow = FAWorkflow.from_config(cfg)
    conv = Conversation()
    context = Context(cfg=cfg, workflow=workflow, conv=conv)
    bot = UIMultiWorkflowBot(cfg=cfg, context=context)
    conv.add_message(msg=msg, role=Role.USER)
    stream = bot.process_stream()
    for chunk in stream:
        print(chunk, end="")
    print()
    bot_output = bot.process_LLM_response()
    print(f"bot_output: {bot_output}")
    print(f"conv: {conv}")
    print()


test_ui_single_bot(msg="挂301医院")
# test_ui_multi_main_bot(msg="帮我挂一个301的号")
# test_ui_multi_workflow_bot(msg="挂一个301的号")
