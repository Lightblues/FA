""" updated @240918
"""

import os, json, tqdm, itertools, pickle, collections, traceback, datetime, argparse, tabulate
from typing import List, Dict, Optional, Tuple, Union
import pandas as pd
import concurrent.futures
from easonsi import utils
# from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL, Config
# from .eval_utils import task_simulate, task_judge, task_judge_2, parse_conv, convert_conv
# from .analyzer import Analyzer
from .eval_utils import task_simulate
from ..main import BaselineController
from ..data import Config, DataManager



class Evaluator:
    cfg: Config = None
    # version: str = None
    # simulation_output_dir: str = None
    
    def __init__(self, cfg: Config):
        self.cfg = cfg
        # self.version = cfg.simulate_version
        # if cfg.to_gsheet: 
        #     from easonsi.files.gsheet import GSheet
        #     self.gsheet = GSheet()
        
    def main(self):
        """ 
        1. run simulations, use `BaselineController(cfg).start_conversation()` to start a single exp with specific config
            output to db with `exp_version` (clean if exist)
        2. run evaluations (query db to find run exps)
        """
        self.print_header_info(step_name="STEP 1.1: Simulating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("simulate")})
        self.run_simulations()

        self.print_header_info(step_name="STEP 2.1: Evaluating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("judge")})
        self.run_evaluations()
        # self.print_header_info(step_name="STEP 2.2: Collecting evaluation results")
        # self.collect_evaluation_results(version="01")
        
        # self.print_header_info(step_name="STEP 2.3: Evaluating V2", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("judge")})
        # self.run_evaluations_v2()
        # self.print_header_info(step_name="STEP 2.4: Collecting evaluation results")
        # self.collect_evaluation_results(version="02")

    @staticmethod
    def print_header_info(step_name: str, infos: Union[None, Dict, pd.DataFrame]=None):
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
            # 1. check if executated (query db)
            # TODO: check if exist
            
            # 2. run with retry (3 times)
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
        conversations = utils.LoadJsonl(self.fn_conversations)
        skipped = set()
        if os.path.exists(self.fn_llmscored_raw):
            existed = utils.LoadJsonl(self.fn_llmscored_raw)
            for d in existed:
                skipped.add((
                    d["workflow_name"], d["workflow_id"]
                ))
        conversations_filtered = [c for c in conversations if (c["workflow_name"], c["workflow_id"]) not in skipped]
        print(f"# of conversations to be judged: {len(conversations_filtered)}")
        
        client = init_client(llm_cfg=LLM_CFG[self.cfg.judge_model_name])
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.cfg.judge_max_workers) as executor:
            futures = []
            for conv in conversations_filtered:
                future = executor.submit(task_judge, conv, self.fn_llmscored_raw, client)
                futures.append(future)
            print(f"Executing {len(futures)} tasks")
            num_errors = 0
            for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
                r = future.result()  # 获取结果以捕获异常并打印错误信息
                if r: num_errors += 1
            print(f"# of errors: {num_errors}")
        if num_errors > 0:
            raise Exception(f"# of errors when evaluation: {num_errors}")

        # Simplify the jsonl format
        df = pd.read_json(self.fn_llmscored_raw, lines=True)
        df.sort_values(["workflow_name", "workflow_id"], inplace=True)
        df_gpt = df[["workflow_name", "workflow_id", "judge_result"]]
        df_gpt.to_json(self.fn_llmscored, orient="records", lines=True, force_ascii=False)

    def collect_evaluation_results(self, version="01"):
        """ 
        FIXED: the eval format checked in `task_judge`
        """
        if version == "01":
            df_labelled_raw = pd.read_json(self.fn_llmscored, lines=True)
            _out_sheeet_name = f"{self.version}_eval"
            _ofn_stat_error = "stat_error_types.png"
            _ofn_stat_score = "stat_scores_overall.png"
        else:
            df_labelled_raw = pd.read_json(self.fn_llmscored_2, lines=True)
            _out_sheeet_name = f"{self.version}_eval_2"
            _ofn_stat_error = "stat_error_types_2.png"
            _ofn_stat_score = "stat_scores_overall_2.png"
        
        # 1) convert to format of doc
        #   cols: [error_types, score, misc]
        converted = []
        for idx, row in df_labelled_raw.iterrows():
            id_ = f"{row['workflow_name']}_{row['workflow_id']:03d}"
            jr = row["judge_result"]
            converted.append((None, jr["overall"]["score"], id_))
            converted.append((None, None, None))
            for turn_id, turn_eval in sorted(jr["detailed"].items(), key=lambda x: int(x[0].split("-")[-1])):
                errors = turn_eval["errors"]
                error_types_str = ",".join(errors.keys() if errors else [])
                converted.append((None, None, turn_id))
                converted.append((error_types_str, turn_eval["score"], str(errors)))
        df_labelled_for_excel = pd.DataFrame(converted, columns=["error_types", "score", "misc"])
        # DONE: concate with formated conversations in `self.fn_conversations_for_labeling`
        
        df_conversation_for_excel = pd.read_csv(self.fn_conversations_for_excel)
        assert len(df_conversation_for_excel) == len(df_labelled_for_excel), f"{len(df_conversation_for_excel)} != {len(df_labelled_for_excel)}"
        _df_out = pd.concat([df_conversation_for_excel, df_labelled_for_excel], axis=1)
        if self.cfg.to_gsheet:  # you can also save to csv
            self.gsheet.to_gsheet(_df_out, sheet_name=_out_sheeet_name)
        
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
        
    def run_evaluations_v2(self):
        _ofn_detailed = self.fn_llmscored_2_raw
        _ofn = self.fn_llmscored_2
        
        conversations = utils.LoadJsonl(self.fn_conversations)
        skipped = set()
        if os.path.exists(_ofn_detailed):
            existed = utils.LoadJsonl(_ofn_detailed)
            for d in existed:
                skipped.add((
                    d["workflow_name"], d["workflow_id"]
                ))
        conversations_filtered = [c for c in conversations if (c["workflow_name"], c["workflow_id"]) not in skipped]
        print(f"# of conversations to be judged: {len(conversations_filtered)}")
        
        client = init_client(llm_cfg=LLM_CFG[self.cfg.judge_model_name])
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.cfg.judge_max_workers) as executor:
            futures = []
            for conv in conversations_filtered:
                future = executor.submit(task_judge_2, conv, _ofn_detailed, client)
                futures.append(future)
            print(f"Executing {len(futures)} tasks")
            num_errors = 0
            for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
                r = future.result()  # 获取结果以捕获异常并打印错误信息
                if r: num_errors += 1
            print(f"# of errors: {num_errors}")
        if num_errors > 0:
            raise Exception(f"# of errors when evaluation: {num_errors}")

        # Simplify the jsonl format
        df = pd.read_json(_ofn_detailed, lines=True)
        df.sort_values(["workflow_name", "workflow_id"], inplace=True)
        df_gpt = df[["workflow_name", "workflow_id", "judge_result"]]
        df_gpt.to_json(_ofn, orient="records", lines=True, force_ascii=False)
