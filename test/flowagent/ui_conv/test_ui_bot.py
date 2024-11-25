""" deprecated! use ss.cfg instead! """
from flowagent.ui_conv.bot_single import PDL_UIBot
from flowagent.data import Config, Conversation, Workflow, DataManager, Role, Message

cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
conv = Conversation()
workflow = Workflow(cfg)

bot = PDL_UIBot(cfg=cfg, conv=conv, workflow=workflow)

conv.add_message(Message(Role.USER, "hello", conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id))
bot.process()
