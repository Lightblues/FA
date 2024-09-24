from flowagent.data import Config, DBManager, BaseLogger, DataManager
from collections import defaultdict

class Stat:
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.db = DBManager(cfg.db_uri, cfg.db_name, cfg.db_message_collection_name)
        self.logger = BaseLogger()
    
    def stat(self, exp_version: str):
        configs = self.db.query_run_experiments({"exp_version": exp_version})
        conversation_ids = [c["conversation_id"] for c in configs]
        # 1. simulate
        
        # 2. judge
        usage = defaultdict(int)
        for cid in conversation_ids:
            res = self.db.query_evaluations({"conversation_id": cid})[0]
            for k,v in res["judge_session_details"]["usage"].items():
                usage[k] += v
        return usage


if __name__ == '__main__':
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    stat = Stat(cfg)
    res = stat.stat("pdl_code_0920")
    print(res)
