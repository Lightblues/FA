from flowagent import Config, DataManager, Judger, Analyzer
from flowagent.data import Conversation, Workflow, Role, Message
from flowagent.roles import ReactBot, CoREBot

def init_react_bot() -> ReactBot:
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.workflow_type = "text"
    cfg.bot_mode = "react_bot"
    
    workflow = Workflow(cfg)
    conv = Conversation()
    bot = ReactBot(cfg=cfg, conv=conv, workflow=workflow)
    return bot

def init_core_bot() -> CoREBot:
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.workflow_type = "core"
    cfg.bot_mode = "core_bot"
    
    workflow = Workflow(cfg)
    conv = Conversation()
    bot = CoREBot(cfg=cfg, conv=conv, workflow=workflow)
    return bot

if __name__ == '__main__':
    # bot = init_react_bot()
    bot = init_core_bot()
    conv = bot.conv
    
    query = "hello"
    conv.add_message(Message(Role.USER, query, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id))
    bot.process()
    print(conv)