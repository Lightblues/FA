""" WARNING: moved to @evaluator.py
@240821 并发模拟, 保存到 $DATA/simulated 下
/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu/data/v240820/simulated/template=query_PDL_jinja_pdl=pdl2_step3_model=qwen2_72B_api=llm/000-114挂号.jsonl

- [ ] 保存CoT信息 (相关meta)
- [ ] 增加偏题的机制 (30% 的概率)
- [ ] 优化 print
- [ ] prompt 优化: 尝试对于API和ANSWER节点分类考虑
- [ ] 优化 EL 部分的系统提示
- [x] 自己部署一下 LLM
- [ ] 实现LLM评分, 比较一致性
- [ ] 保存 meta 信息 #P1
"""
import os, argparse, json, tqdm, traceback
import concurrent.futures
from simulator.simulator_with_profile import SimulatorV2
from engine import (
    Conversation, Config, _DIRECTORY_MANAGER, DataManager, UserProfile
)
from easonsi import utils


def task(cfg, user_profile_json, workflow_name, ofn):
    fp = open(ofn, "a+", encoding="utf-8")
    
    user_profile = UserProfile.load_from_dict(user_profile_json)
    
    # 2] Initialize the simulator
    simulator = SimulatorV2(cfg)

    # 3] Run the simulation with the ref_conversation
    infos, conversation = simulator.start_simulation(user_profile)
    simulated_res = {
        "workflow_name": workflow_name,
        "simulated_conversation": conversation.to_str(),
        "user_profile": user_profile.to_str(),
        "meta_infos": infos,
    }
    fp.write(json.dumps(simulated_res, ensure_ascii=False)+"\n")
    fp.flush()
    fp.close()
    return simulated_res


def run_single_simulation_mp(cfg:Config, workflow_name:str, odir:str, num_persona=15, exec=True, debug=False):
    """ Run simulation for a specific workflow
    input:
        -> load workflow from $workflow_dir/$workflow_name.yaml
        -> load persona from $DIR_user_profile/$workflow_name.json
    """
    os.makedirs(odir, exist_ok=True)
    ofn = f"{odir}/{workflow_name}.jsonl"
    generated_profiles = []
    if os.path.exists(ofn):
        print(f"[warning] {ofn} exists!")
        _d = utils.LoadJsonl(ofn)
        generated_profiles = [d['user_profile'] for d in _d]
    
    assert cfg.workflow_name == workflow_name, f"{cfg.workflow_name} != {workflow_name}"

    fn = _DIRECTORY_MANAGER.DIR_user_profile / f"{workflow_name}.json"
    with open(fn, "r") as f:
        user_profile_jsons = json.load(f)
    user_profile_jsons = user_profile_jsons[:num_persona]       # NOTE: select the first 15 personas
    user_profile_jsons = [i for i in user_profile_jsons if not any(i["persona"] in p for p in generated_profiles)]
    
    if exec:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for up in user_profile_jsons:
                future = executor.submit(task, cfg, up, workflow_name, ofn)
                futures.append(future)
            for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Running simulations"):
                future.result()  # 获取结果以捕获异常并打印错误信息
    else:
        tasks = []
        for up in user_profile_jsons:
            tasks.append((cfg, up, workflow_name, ofn))
        return tasks

def run_simulations_mp(base_cfg:Config, workflow_names, output_dir=_DIRECTORY_MANAGER.DIR_simulation/"tmp", max_workers=10):
    tasks = []
    for workflow_name in workflow_names:
        cfg = base_cfg.copy()
        cfg.workflow_name = workflow_name     # NOTE: update the config.workflow_name
        tasks.extend(run_single_simulation_mp(cfg, workflow_name, output_dir, exec=False))

    def f_exec(cfg, up, workflow_name, ofn):
        try:
            return task(cfg, up, workflow_name, ofn)
        except Exception as e:
            print(f"Task failed for {up}: {e}")
            traceback.print_exc()
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for cfg, up, workflow_name, ofn in tasks:
            future = executor.submit(f_exec, cfg, up, workflow_name, ofn)
            futures.append(future)

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Executing tasks"):
            future.result()  # 获取结果以捕获异常并打印错误信息


if __name__ == '__main__':
    # --- config overwrite ---
    max_workers = 10
    # max_workers = 1
    model_name = "v0729-Llama3_1-70B"
    
    cfg = Config.from_yaml(DataManager.normalize_config_name("simulate.yaml"))
    cfg.model_name = model_name
    cfg.normalize_paths()       # fix the path
    
    _pdl_version = os.path.split(cfg.workflow_dir)[-1]
    # "template=query_PDL_jinja_pdl=pdl2_step3_model=qwen2_72B_api=llm"
    VERSION = f"0828_template={cfg.template_fn}_pdl={_pdl_version}_bot={cfg.bot_mode}_model={cfg.model_name}_api={cfg.api_mode}"
    VERSION = VERSION.replace("/", "_").replace(".", "_")
    odir = _DIRECTORY_MANAGER.DIR_simulation / VERSION
    
    # MODE = "single"
    MODE = "all"
    if MODE == "single":
        # --- run single ---
        workflow_name = "001-注册邀约"
        workflow_name = "002-新闻查询"
        workflow_name = "025-酒店取消订单"
        workflow_name = "000-114挂号"
        cfg.workflow_name = workflow_name
        res = run_single_simulation_mp(cfg, workflow_name, odir)
    elif MODE == "all":
        # --- run all ---
        # workflow_names = DataManager.get_workflow_name_list(_DIRECTORY_MANAGER.DIR_user_profile, extension=".json")
        workflow_names = ['000-114挂号', "002-新闻查询", '019-礼金礼卡类案件', '023-查号源日期', '025-酒店取消订单']  # '001-注册邀约', 
        # workflow_names = ['003-物品能否邮寄', '005-课程调整', '006-同程开发票', '007-门诊费用报销', '008-寄快递', '012-就诊预约咨询']
        print(f"workflow_names: {workflow_names}")
        
        run_simulations_mp(base_cfg=cfg, workflow_names=workflow_names, output_dir=odir, max_workers=max_workers)
    else:
        raise ValueError(f"Unknown MODE: {MODE}")
