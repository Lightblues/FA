from flowagent import Config, DataManager, FlowagentConversationManager
from flowagent.data import Conversation, Workflow, Role, Message
from flowagent.roles import ReactBot, CoREBot, PDLBot

cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
cfg.simulate_force_rerun = True

cfg.user_mode = "llm_oow"
cfg.user_oow_ratio = 0.8
cfg.user_profile_id = 0
cfg.workflow_id = "002"

# react
mode = "core"
if mode == "react":
    cfg.workflow_type = "text"
    cfg.bot_mode = "react_bot"
elif mode == "core":
    cfg.workflow_type = "core"
    cfg.bot_mode = "core_bot"
elif mode == "pdl":
    cfg.workflow_type = "pdl"
    cfg.bot_mode = "pdl_bot"


if __name__ == '__main__':
    controller = FlowagentConversationManager(cfg)
    conv = controller.conversation(verbose=True)
    print(conv)