""" 
统一评估流程: @240828
1. 调用simulator完成制定数量的会话; 
2. 整合结果, 格式化输出;
3. 集中化评估, 格式化输出;

- [ ] 保存CoT信息 (相关meta)    #P2
- [x] 增加偏题的机制 (30% 的概率) -- 在persona中
- 优化输出
    - [x] 整个 evaluation 过程中的 print
    - [ ] 简化 simulateion 过程中的输出
    - [ ] 优化 EL 部分的系统提示
- [x] prompt 优化: 尝试对于API和ANSWER节点分类考虑
    有待评估效果
- [x] 实现LLM评分, 比较一致性
- [ ] 保存 meta 信息 #P1
- [x] BUG: LLM evaluation 可视化结果和turns没有对上 #P1

output: 
    https://doc.weixin.qq.com/sheet/e3_Aa8AFwbhAEsNvUX5XUlTXSTGWsT5A?scode=AJEAIQdfAAok83fN9fAcMATAZtAPI&tab=d88els
"""

import os, json, tqdm, itertools, pickle, collections, traceback, datetime, argparse, tabulate
from typing import List, Dict, Optional, Tuple, Union
import pandas as pd
import concurrent.futures
from easonsi import utils
from engine import _DIRECTORY_MANAGER, LLM_CFG, init_client, PDL, Config
from .eval_utils import task_simulate, task_judge, task_judge_2, parse_conv, convert_conv
from .analyzer import Analyzer



class Evaluator:
    cfg: Config = None
    version: str = None
    simulation_output_dir: str = None
    def __init__(self, cfg: Config):
        cfg.model_name = cfg.simulate_model_name # fix the model name?
        cfg.normalize_paths()       # fix the path
        if not cfg.simulate_version:
            # set as `v240828` by default | datetime
            default_version = datetime.datetime.now().strftime("%Y%m%d")
            cfg.simulate_version = f"v{default_version}"
        self.cfg = cfg
        self.version = cfg.simulate_version
        self.simulation_output_dir = _DIRECTORY_MANAGER.DIR_simulation / cfg.simulate_version
        self.fn_conversations_for_excel = self.simulation_output_dir / "simulated_conversations.csv"
        self.fn_conversations = self.simulation_output_dir / "simulated_conversations.jsonl"
        
        self.judger_output_dir = self.simulation_output_dir / self.cfg.judge_model_name
        os.makedirs(self.judger_output_dir, exist_ok=True)
        self.fn_llmscored_raw = self.judger_output_dir / "eval_gpt_detailed.jsonl"
        self.fn_llmscored = self.judger_output_dir / "eval_gpt.jsonl"      # simplified
        self.fn_llmscored_2_raw = self.judger_output_dir / "eval_gpt_2_detailed.jsonl"
        self.fn_llmscored_2 = self.judger_output_dir / "eval_gpt_2.jsonl"      # simplified
        if cfg.to_gsheet: 
            from easonsi.files.gsheet import GSheet
            self.gsheet = GSheet()
        
    def main(self):
        # 
        self.print_header_info(step_name="STEP 1.1: Simulating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("simulate")})
        self.run_simulations()
        self.print_header_info(step_name="STEP 1.2: Collecting simulated results")
        self.collect_simulated_results()    # If error, check step one!

        self.print_header_info(step_name="STEP 2.1: Evaluating", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("judge")})
        self.run_evaluations()
        self.print_header_info(step_name="STEP 2.2: Collecting evaluation results")
        self.collect_evaluation_results(version="01")
        
        self.print_header_info(step_name="STEP 2.3: Evaluating V2", infos={k:v for k,v in self.cfg.to_dict().items() if k.startswith("judge")})
        self.run_evaluations_v2()
        self.print_header_info(step_name="STEP 2.4: Collecting evaluation results")
        self.collect_evaluation_results(version="02")

    def print_header_info(self, step_name: str, infos: Union[None, Dict, pd.DataFrame]=None):
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
        # config: simulate_*
        tasks = []
        for workflow_name in self.cfg.simulate_workflow_names:
            cfg = self.cfg.copy()
            cfg.workflow_name = workflow_name     # NOTE: update the config.workflow_name
            tasks.extend(self.run_single_simulation_mp(cfg, workflow_name, self.simulation_output_dir, num_persona=self.cfg.simulate_persons_per_workflow, exec=False))

        def f_exec(cfg, up, workflow_name, ofn):
            for retry_ in range(3):
                try:
                    return task_simulate(cfg, up, workflow_name, ofn)
                except Exception as e:
                    print(f"Task failed for {up}: {e}")
                    traceback.print_exc()
            else:
                print(f"ERROR!!! Task failed after 3 retrys for {up}")
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.cfg.simulate_max_workers) as executor:
            futures = []
            for cfg, up, workflow_name, ofn in tasks:
                future = executor.submit(f_exec, cfg, up, workflow_name, ofn)
                futures.append(future)

            for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
                future.result()  # 获取结果以捕获异常并打印错误信息
    
    @staticmethod
    def run_single_simulation_mp(cfg:Config, workflow_name:str, odir:str, num_persona=-1, max_workers=10, exec=True, debug=False):
        """ Run simulation for a specific workflow
        input:
            -> load workflow from $workflow_dir/$workflow_name.yaml
            -> load persona from $DIR_user_profile/$workflow_name.json
        """
        assert cfg.workflow_name == workflow_name, f"{cfg.workflow_name} != {workflow_name}"
        
        os.makedirs(odir, exist_ok=True)
        ofn = f"{odir}/{workflow_name}.jsonl"
        generated_profiles = []
        if os.path.exists(ofn):
            print(f"[warning] {ofn} exists!")
            _d = utils.LoadJsonl(ofn)
            generated_profiles = [d['user_profile'] for d in _d]

        fn = _DIRECTORY_MANAGER.DIR_user_profile / f"{workflow_name}.json"
        with open(fn, "r") as f:
            user_profile_jsons = json.load(f)
        if num_persona > 0:
            user_profile_jsons = user_profile_jsons[:num_persona]
        user_profile_jsons = [i for i in user_profile_jsons if not any(i["persona"] in p for p in generated_profiles)]
        
        if exec:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for up in user_profile_jsons:
                    future = executor.submit(task_simulate, cfg, up, workflow_name, ofn)
                    futures.append(future)
                for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Running simulations"):
                    future.result()  # 获取结果以捕获异常并打印错误信息
        else:
            tasks = []
            for up in user_profile_jsons:
                tasks.append((cfg, up, workflow_name, ofn))
            return tasks
    
    
    @staticmethod
    def sort_file(workflow_name:str, output_dir: str):
        # 按照 User_profile 的顺序, 对于生成结果排序
        simulated = utils.LoadJsonl(output_dir / f"{workflow_name}.jsonl")
        uprofiles = utils.LoadJson(_DIRECTORY_MANAGER.DIR_user_profile / f"{workflow_name}.json")
        persona_to_idx = {p["persona"]:i for i,p in enumerate(uprofiles)}
        sorted_data = []
        for _,s in enumerate(simulated):
            for p,idx in persona_to_idx.items():
                if p in s["user_profile"]:
                    sorted_data.append((idx, s))
                    break
            else:
                raise ValueError(f"Unknown persona: {s['user_profile']}")
        sorted_data = sorted(sorted_data, key=lambda x: x[0])
        assert [d[0] for d in sorted_data] == list(range(len(sorted_data)))  # check that all data are generated
        sorted_data = [d[1] for d in sorted_data]
        assert len(sorted_data) == len(simulated)
        utils.SaveJsonl(sorted_data, output_dir / f"{workflow_name}.jsonl")
        return sorted_data

    def collect_simulated_results(self):
        # 1) sort the simulated results
        fns = sorted(os.listdir(self.simulation_output_dir))
        fns = [fn for fn in fns if fn.endswith(".jsonl") and fn.startswith("0")]
        workflow_names = [fn[:-len(".jsonl")] for fn in fns]
        for workflow_name in tqdm.tqdm(workflow_names, desc="Collecting simulated results"):
            self.sort_file(workflow_name, self.simulation_output_dir)

        # 2) convert to U/I utterance format (two columns)
        # 对于每一组对话, 第一行为meta信息, 第二行为bot  greeting, 后面的 U/B 之间的会话
        def fn_collect():
            parsed_data = []
            for fn in fns:
                data = utils.LoadJsonl(self.simulation_output_dir / fn)
                print(f"{fn}: {len(data)}")
                for i,sample_d in enumerate(data):
                    parsed_data.append(
                        (f'{sample_d["workflow_name"]}_{i:03d}', sample_d["user_profile"])
                    )
                    conv = parse_conv(sample_d["simulated_conversation"])  # split conversation str into `utterance` of user/bot
                    parsed_data.append(("START", conv[0]))
                    for j,ssample_str in enumerate(conv[1:]):
                        role = "USER" if j % 2 == 0 else "BOT"
                        parsed_data.append((f"{role}-{j//2+1}", ssample_str))
                    # check len(simulated_conversation) is odd? DONE in `parse_conv`

            df = pd.DataFrame(parsed_data, columns=["turn", "content"])
            df.to_csv(self.fn_conversations_for_excel, index=False)
            if self.cfg.to_gsheet:
                self.gsheet.to_gsheet(df, sheet_name=f"{self.version}_sim")
            return df
        def check_exist():  # ugly code for acceleration
            if not os.path.exists(self.fn_conversations_for_excel): return False
            num_conversations = sum(
                len(utils.LoadJsonl(self.simulation_output_dir / fn)) for fn in fns
            )
            df = pd.read_csv(self.fn_conversations_for_excel)
            num_existed = len(df)
            return num_conversations == num_existed
        if not check_exist():
            df = fn_collect()
        else:
            df = pd.read_csv(self.fn_conversations_for_excel)
    
        # 3) convert to standard format
        # 转为规范的数据格式, {workflow_name, workflow_id, user_profile, simulated_conversation}
        conversations = convert_conv(df)
        utils.SaveJsonl(conversations, self.fn_conversations)
    
        ssample_str = tabulate.tabulate(
            conversations[0]["simulated_conversation"],  headers=["turn", "content"],
            showindex=False, maxcolwidths=150, tablefmt="psql") # headers="keys", simple_outline/psql
        print(f"sample conversation from {conversations[0]['workflow_name']}:\n{ssample_str}")

    def run_evaluations(self):
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
