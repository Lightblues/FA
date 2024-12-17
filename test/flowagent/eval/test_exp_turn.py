from flowagent import Config, DataManager, Evaluator


if __name__ == "__main__":
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.workflow_dataset = "PDL_zh"
    cfg.exp_mode = "turn"
    cfg.exp_version = "test_turn"
    # cfg.user_mode = "manual"
    cfg.simulate_max_workers = 1
    cfg.simulate_num_persona = 1
    # cfg.judge_max_workers = 1
    cfg.judge_log_to = None  # not to wandb

    controller = Evaluator(cfg)
    controller.main()
