from flowagent import Config, DataManager, FlowagentConversationManager


cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))

cfg.workflow_dataset = "PDL_zh"
cfg.workflow_id = "000"
cfg.workflow_type = "pdl"


def init_manual(cfg: Config) -> Config:
    cfg.user_mode = "manual"
    cfg.api_mode = "v01"
    cfg.bot_mode = "pdl_bot"
    cfg.bot_template_fn = "flowagent/bot_pdl.jinja"
    return cfg


cfg = init_manual(cfg)
controller = FlowagentConversationManager(cfg)
controller.conversation(verbose=True)
