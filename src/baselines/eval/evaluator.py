""" updated @240918
"""

import os, json, tqdm, itertools, pickle, collections, traceback, datetime, argparse, tabulate
from typing import List, Dict, Optional, Tuple, Union
import pandas as pd
import concurrent.futures
from easonsi import utils

from .eval_utils import task_simulate, task_judge
from ..main import BaselineController
from ..data import Config, DataManager, DBManager



class Evaluator:
    cfg: Config = None
    data_namager: DataManager = None
    # version: str = None
    # simulation_output_dir: str = None
    
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.data_namager = DataManager(cfg)
        # self.version = cfg.simulate_version
        # if cfg.to_gsheet: 
        #     from easonsi.files.gsheet import GSheet
        #     self.gsheet = GSheet()
        
    def main(self):
        """ 
        0. set configs. log the configs by `exp_version`
        1. run simulations, use `BaselineController(cfg).start_conversation()` to start a single exp with specific config
            output to db with `exp_version` (clean if exist)
        2. run evaluations (query db to find run exps)
        """
        self.process_configs()
        
        self.print_header_info(step_name="STEP 1: Simulating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("simulate")})
        self.run_simulations()

        self.print_header_info(step_name="STEP 2.1: Evaluating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("judge")})
        self.run_evaluations()
        # self.print_header_info(step_name="STEP 2.2: Collecting evaluation results")
        # self.collect_evaluation_results(version="01")
        
        # self.print_header_info(step_name="STEP 2.3: Evaluating V2", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("judge")})
        # self.run_evaluations_v2()
        # self.print_header_info(step_name="STEP 2.4: Collecting evaluation results")
        # self.collect_evaluation_results(version="02")
    
    def process_configs(self):
        """ Log the config. If existed, reload it! """
        cfn_fn = self.data_namager.DIR_engine_config / f"exps/{self.cfg.exp_version}.yaml"
        os.makedirs(cfn_fn.parent, exist_ok=True)
        if os.path.exists(cfn_fn):
            print(f"EXP {self.cfg.exp_version} config existed! Loading from {cfn_fn}")
            self.cfg = Config.from_yaml(cfn_fn)     # NOTE: reload the config!
        else:
            self.cfg.to_yaml(cfn_fn)
            print(f"EXP {self.cfg.exp_version} config saved to {cfn_fn}")

    @staticmethod
    def print_header_info(step_name: str, infos: Union[None, Dict, pd.DataFrame]=None):
        """ Formatted header info """
        step_name = f" {step_name.strip()} "
        s_print = step_name.center(150, "=") + "\n"
        if infos is not None:
            if isinstance(infos, dict):
                infos = pd.DataFrame([infos]).T
            elif isinstance(infos, pd.DataFrame):
                pass
            else:
                raise NotImplementedError
            s_infos = tabulate.tabulate(infos, tablefmt='psql')    # , headers='keys', 
            s_print += f"--- infos ---\n{s_infos}\n"
        s_print += "-"*150
        print(s_print)

    def run_simulations(self):
        """ 
        1. get all the simulation configs
        2. run simulations in parallel
        """
        def f_exec(cfg):
            # 1. check if run (query db) -- DONE in `BaselineController.start_conversation`
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
        user_profiles = BaselineController(cfg).workflow.user_profiles
        num_user_profile = len(user_profiles)
        if simulate_num_persona is not None and simulate_num_persona > 0:
            num_user_profile = min(num_user_profile, simulate_num_persona)
        # 2. get all the configs
        tasks = []
        for uid in range(num_user_profile):
            cfg_new = cfg.copy()
            cfg_new.user_profile_id = uid
            tasks.append((cfg))
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
        """ 
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

    @staticmethod
    def get_evaluation_configs(cfg:Config):
        """filter the experiments by `exp_version`
        """
        # 1. find all run experiments
        db = DBManager(cfg.db_uri, cfg.db_name, cfg.db_message_collection_name)
        query = {
            "exp_version": cfg.exp_version
        }
        run_exps = db.query_run_experiments(query, limit=0)
        
        # 2. write all exp configs to a new cfg
        tasks = []
        for exp in run_exps:
            cfg_new = cfg.copy()
            cfg_new.judge_conversation_id = exp["conversation_id"]
            # TODO: check the configs
            tasks.append(cfg_new)
        return tasks

    def collect_evaluation_results(self):
        """ 
        FIXED: the eval format checked in `task_judge`
        """
        
        # 1) convert to format of doc
        #   cols: [error_types, score, misc]

        # 2) analyze
        analyzer = Analyzer(df_labelled_raw, output_dir=self.judger_output_dir)
        _num_workflows = len(df_labelled_raw["workflow_name"].unique())
        stat_dict = {
            "num_workflows": _num_workflows,
            "support": len(df_labelled_raw) // _num_workflows
        }
        _ = analyzer.stat_num_turns(stat_dict=stat_dict)
        _ = analyzer.stat_scores_overall(th=self.cfg.judge_passrate_threshold, ofn=_ofn_stat_score, stat_dict=stat_dict)
        _ = analyzer.stat_error_types(ofn=_ofn_stat_error)
        df_grouped_passrate = analyzer.stat_grouped_passrate(th=self.cfg.judge_passrate_threshold).round(3)
        df_stats = pd.DataFrame([stat_dict]).T.round(3) \
            .reset_index().rename(columns={"index": "key", 0: "value"})
        print(f"--- stats ---\n" + tabulate.tabulate(df_stats, tablefmt='psql'))
        print(f"--- grouped passrate ---\n" + tabulate.tabulate(df_grouped_passrate, tablefmt='psql'))
        
        # useful to copy and paste into Excel??
        # grouped_passrate = grouped_passrate.round(3)
        # tabbed_str = "\t".join(grouped_passrate.columns) + "\n" + "\n".join(["\t".join(map(str, row)) for row in grouped_passrate.values])
        # print(tabbed_str)
