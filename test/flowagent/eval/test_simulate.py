""" test a single simulation/exp """
from flowagent import Config, DataManager, FlowagentConversationManager

if __name__ == '__main__':
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.simulate_force_rerun = True
    cfg.user_mode = "llm_oow"
    cfg.user_oow_ratio = 0.8
    # ---
    cfg.workflow_type = "pdl"
    cfg.bot_mode = "pdl_bot"
    # ---
    cfg.user_profile_id = 0
    # cfg.workflow_id = "001"
    cfg.workflow_id = "002"
    controller = FlowagentConversationManager(cfg)
    controller.start_conversation(verbose=True)
