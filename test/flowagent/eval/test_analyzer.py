from flowagent import Config, DataManager, Judger, Analyzer

if __name__ == '__main__':
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.exp_mode = "turn"
    cfg.exp_version = "test_turn"
    cfg.judge_log_to = None # not to wandb

    analyzer = Analyzer(cfg)
    out = analyzer.analyze()
    print(out)
