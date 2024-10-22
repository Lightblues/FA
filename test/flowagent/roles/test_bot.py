from flowagent import Config, DataManager, Judger, Analyzer
from flowagent.data import Conversation, Workflow, Role, Message
from flowagent.roles import ReactBot

if __name__ == '__main__':
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    workflow = Workflow(cfg)
    conv = Conversation()
    
    bot = ReactBot(cfg=cfg, conv=conv, workflow=workflow)
    
    query = "hello"
    conv.add_message(Message(Role.USER, query, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id))
    bot.process()
    print(conv)