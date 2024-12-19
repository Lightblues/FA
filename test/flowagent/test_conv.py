from common import Config
from flowagent import FlowagentConversationManager


cfg = Config.from_yaml("default.yaml")
cfg.simulate_force_rerun = True

cfg.workflow_dataset = "PDL_zh"
cfg.workflow_id = "000"

user_mode = "llm_profile"
if user_mode == "manual":
    cfg.user_mode = "manual"
elif user_mode == "llm_profile":
    cfg.user_mode = "llm_profile"
    cfg.user_oow_ratio = 0.8
    cfg.user_profile_id = 2

mode = "pdl"
if mode == "react":
    cfg.workflow_type = "text"
    cfg.bot_mode = "react_bot"
elif mode == "core":
    cfg.workflow_type = "core"
    cfg.bot_mode = "core_bot"
    cfg.api_mode = "core"
elif mode == "pdl":
    cfg.workflow_type = "pdl"
    cfg.bot_mode = "pdl_bot"


if __name__ == "__main__":
    controller = FlowagentConversationManager(cfg)
    conv = controller.conversation(verbose=True)
    print(conv)
