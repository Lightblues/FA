""" refresh experiment judge results """

import tqdm, concurrent.futures, itertools
from typing import Callable
from flowagent.eval import EvalUtils
from flowagent import DataManager, Config, Judger, DBManager


def run_evaluations(f_task: Callable, cfg: Config):
    """ evaluation process:
    1. get the experiments to be evaluated
    2. run evaluations in parallel
    """
    tasks = EvalUtils.get_evaluation_configs(cfg)
    with concurrent.futures.ThreadPoolExecutor(max_workers=cfg.judge_max_workers) as executor:
        futures = []
        for c in tasks:
            c.judge_force_rejudge = True        # force rejudge
            future = executor.submit(f_task, c)
            futures.append(future)
        print(f"Executing {len(futures)} judge tasks...")
        num_errors = 0
        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
            r = future.result() 
            if r: num_errors += 1
        print(f"# of errors: {num_errors}")

def task_judge_turn_level(cfg: Config) -> None:
    def check(): # check whether need to be rejudged
        db = DBManager(cfg.db_uri, cfg.db_name, cfg.db_message_collection_name)
        query_res = db.query_evaluations({ "conversation_id": cfg.judge_conversation_id })
        if len(query_res) == 0: return True
        if "type" not in query_res[0]["judge_turn_result"][0]: return True
        else: return False
    if check():
        judger = Judger(cfg)
        judger.start_judge(verbose=False, mode="turn")


if __name__ == '__main__':
    model = "Qwen2-72B"
    selected_formats = ['text', 'code', 'flowchart', 'pdl-pdl']
    selected_datasets = ['sgd', 'pdl', 'star']
    for format, dataset in itertools.product(selected_formats, selected_datasets):
        exp_version = f"turn_{dataset}_{format}_{model}"
        print(f">> rejudging: {exp_version}")
        
        cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
        cfg.judge_force_rejudge = True  # force rejudge
        cfg.exp_version = exp_version
        cfg.exp_mode = "turn"
        cfg.workflow_dataset = dataset.upper()
        cfg.workflow_type = format if (not format.startswith("pdl")) else 'pdl'
    
        run_evaluations(task_judge_turn_level, cfg)