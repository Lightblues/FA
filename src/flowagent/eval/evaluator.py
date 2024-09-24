""" Main entrypoint for evaluation! run simulations, judge, and analyze
updated @240918

- [ ] add stat of #error_output (for parse)
- [ ] turn-level evaluation
- [ ] update analyzer: more metrics
"""

import os, json, tqdm, itertools, pickle, collections, traceback, datetime, argparse
from typing import List, Dict, Optional, Tuple, Union
import pandas as pd
import concurrent.futures
from easonsi import utils

from .eval_utils import task_simulate, task_judge
from ..controller import FlowbenchController
from ..data import Config, DataManager, DBManager, LogUtils
from .analyzer import Analyzer


class Evaluator:
    """ abstraction of whole evaluation process
    USAGE:
        evaluator = Evaluator(cfg)
        evaluator.main()
    """
    cfg: Config = None
    data_namager: DataManager = None
    db: DBManager = None
    
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.data_namager = DataManager(cfg)
        self.db = DBManager(cfg.db_uri, cfg.db_name, cfg.db_message_collection_name)
        
    def main(self):
        """ 
        0. set configs. log the configs by `exp_version`
        1. run simulations, use `XXXController(cfg).start_conversation()` to start a single exp with specific config
            output to db with `exp_version` (clean if exist)
        2. run evaluations/judges (query db to find run exps)
        3. analyze the evaluation results
        """
        self.process_configs()
        
        self.print_header_info(step_name="STEP 1: Simulating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("simulate") or k.startswith("exp")})
        self.run_simulations()

        self.print_header_info(step_name="STEP 2: Evaluating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("judge")})
        self.run_evaluations()
        
        self.print_header_info(step_name="STEP 3: Analyzing")
        self.analyze()
    
    def process_configs(self):
        """ Log the config. If existed, reload it! """
        cfn_fn = self.data_namager.DIR_config / f"exps/{self.cfg.exp_version}.yaml"
        os.makedirs(cfn_fn.parent, exist_ok=True)
        if os.path.exists(cfn_fn):
            print(f"EXP {self.cfg.exp_version} config existed! Loading from {cfn_fn}")
            self.cfg = Config.from_yaml(cfn_fn)     # NOTE: reload the config!
        else:
            if self.cfg.exp_save_config: # save the config
                self.cfg.to_yaml(cfn_fn)
                print(f"EXP {self.cfg.exp_version} config saved to {cfn_fn}")

    @staticmethod
    def print_header_info(step_name: str, infos: Union[None, Dict, pd.DataFrame]=None):
        """ Formatted header info """
        step_name = f" {step_name.strip()} "
        s_print = step_name.center(150, "=") + "\n"
        if infos is not None:
            s_print += LogUtils.format_infos_with_tabulate(infos)
        print(s_print)

    def run_simulations(self):
        """ 
        1. get all the simulation configs
        2. run simulations in parallel
        """
        def f_exec(cfg):
            # 1. check if run (query db) -- DONE in `XXXController.start_conversation`
            # 2. run with retry (3 times) NOTE: can be a decorator? 
            for retry_ in range(3):
                try:
                    return task_simulate(cfg)
                except Exception as e:
                    print(f"Task failed for {cfg}: {e}")
                    traceback.print_exc()
            else:
                print(f"ERROR!!! Task failed after 3 retrys for {cfg}")
                return None

        tasks = self.get_configs_all_workflows(self.cfg, simulate_num_persona=self.cfg.simulate_num_persona)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.cfg.simulate_max_workers) as executor:
            futures = []
            for cfg in tasks:
                future = executor.submit(f_exec, cfg)
                futures.append(future)
            print(f"Running {len(futures)} tasks...")
            for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
                future.result()  # 获取结果以捕获异常并打印错误信息
    
    @staticmethod
    def get_configs_per_workflow(cfg:Config, simulate_num_persona:int=None):
        """ Run simulation for a specific workflow
        """
        # 1. get all user ids
        user_profiles = FlowbenchController(cfg).workflow.user_profiles
        num_user_profile = len(user_profiles)
        if simulate_num_persona is not None and simulate_num_persona > 0:
            num_user_profile = min(num_user_profile, simulate_num_persona)
        # 2. get all the configs
        tasks = []
        for uid in range(num_user_profile):
            cfg_new = cfg.copy()
            cfg_new.user_profile_id = uid
            tasks.append((cfg_new))
        return tasks
    
    @staticmethod
    def get_configs_all_workflows(cfg:Config, simulate_num_persona:int=None, workflow_ids: List[str]=None):
        """ Run simulation for all workflows
        """
        # 1. get all workflow_ids
        if workflow_ids is None:
            num_workflow = DataManager(cfg).num_workflows
            workflow_ids = [f"{i:03d}" for i in range(num_workflow)]
        # 2. get all the configs
        tasks = []
        for workflow_id in workflow_ids:
            cfg_new = cfg.copy()
            cfg_new.workflow_id = workflow_id
            tasks.extend(Evaluator.get_configs_per_workflow(cfg_new, simulate_num_persona=simulate_num_persona))
        return tasks
    


    def run_evaluations(self):
        """ evaluation process:
        1. get the experiments to be evaluated
        2. run evaluations in parallel
        """
        tasks = self.get_evaluation_configs(self.cfg)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.cfg.judge_max_workers) as executor:
            futures = []
            for cfg in tasks:
                future = executor.submit(task_judge, cfg)
                futures.append(future)
            print(f"Executing {len(futures)} judge tasks...")
            num_errors = 0
            for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
                r = future.result()  # 获取结果以捕获异常并打印错误信息
                if r: num_errors += 1
            print(f"# of errors: {num_errors}")
        if num_errors > 0:
            raise Exception(f"# of errors when evaluation: {num_errors}")

    def get_evaluation_configs(self, cfg:Config):
        """filter the experiments by `exp_version`
        """
        # 1. find all run experiments
        query = {
            "exp_version": cfg.exp_version
        }
        run_exps = self.db.query_run_experiments(query, limit=0)
        
        # 2. get all evaluation configs
        tasks = []
        for exp in run_exps:
            # 2.1 restore the exp config
            cfg_exp = Config.from_dict(
                self.db.query_config_by_conversation_id(exp["conversation_id"])
            )
            # 2.2 check if the configs of run exps match the input config. partly done by the "reloading" mechanism?
            keys_to_check = ["exp_version", "workflow_dataset", "workflow_type"]
            assert all([cfg_exp[k] == cfg[k] for k in keys_to_check]), f"Config mismatch: {cfg_exp} vs {cfg}"
            # 2.3 ensure the judge config slots: `judge_conversation_id, judge_model_name`
            cfg_exp.judge_model_name = cfg.judge_model_name
            cfg_exp.judge_conversation_id = exp["conversation_id"]
            tasks.append(cfg_exp)
        return tasks

    def analyze(self):
        """ analysis process: -> to `Analyzer`
        """
        analyzer = Analyzer(self.cfg)
        analyzer.analyze()
