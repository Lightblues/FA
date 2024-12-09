from flowagent import Config, DataManager, Judger, Analyzer
from flowagent.data import Conversation, Workflow, Role, Message
from flowagent.roles import ReactBot, CoREBot, PDLBot, UISingleBot

def init_ui_bot() -> UISingleBot:
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.workflow_type = "pdl"
    cfg.bot_mode = "pdl_bot"
    cfg.workflow_dataset = "PDL_zh"
    cfg.workflow_type = "pdl"
    
    workflow = Workflow(cfg)
    conv = Conversation()
    bot = UISingleBot(cfg=cfg, conv=conv, workflow=workflow)
    return bot

if __name__ == '__main__':
    bot = init_ui_bot()
    conv = bot.conv
    query = "hello"
    conv.add_message(Message(role=Role.USER, content=query, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id))
    prompt, stream = bot.process_stream()
    llm_response = ""
    for chunk in stream:
        llm_response += chunk
        print(chunk, end="")
    print()
    bot_output = bot.process_LLM_response(prompt, llm_response)
    print(bot_output)
    print(conv)