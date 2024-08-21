""" 
@240723 并发模拟, 保存到 $DATA/simulated 下
/apdcephfs_cq8/share_2992827/shennong_5/easonsshi/huabu/data/v240820/simulated/template=query_PDL_jinja_pdl=pdl2_step3_model=qwen2_72B_api=llm/000-114挂号.jsonl

- [ ] 保存CoT信息 (相关meta)
- [ ] 增加偏题的机制 (30% 的概率)
- [ ] 优化 print
- [ ] 尝试对于API和ANSWER节点分类考虑
- [ ] 优化 EL 部分的系统提示
- [ ] 自己部署一下 LLM
- [ ] config add shown PDLs
"""
import os, argparse, json, tqdm
import concurrent.futures
from simulator.simulator_with_profile import SimulatorV2
from engine import (
    Conversation, Config, _DIRECTORY_MANAGER, DataManager, UserProfile
)
from easonsi import utils


def run_single_simulation(cfg:Config, workflow_name:str, odir:str=_DIRECTORY_MANAGER.DIR_simulated_base/"tmp", debug=False):
    """ Run simulation for a specific workflow
    input:
        workflow_name: str
        -> load workflow from $workflow_dir/$workflow_name
        -> load predetermined conversation from $workflow_dir/$workflow_name.json
    """
    # 0] Check if the simulation result exists
    os.makedirs(odir, exist_ok=True)
    ofn = f"{odir}/{workflow_name}.jsonl"
    generated_profiles = []
    if os.path.exists(ofn):
        print(f"[warning] {ofn} exists!")
        _d = utils.LoadJsonl(ofn)
        generated_profiles = [d['user_profile'] for d in _d]
    fp = open(ofn, "a+", encoding="utf-8")
    
    assert cfg.workflow_name == workflow_name, f"{cfg.workflow_name} != {workflow_name}"
    simulated_results = []
    # 1] Load the LLM-generated conversation
    # fn = f"{_DIRECTORY_MANAGER.DIR_conversation_v1}/{workflow_name}.json"
    fn = _DIRECTORY_MANAGER.DIR_user_profile / f"{workflow_name}.json"
    with open(fn, "r") as f:
        user_profile_jsons = json.load(f)
    user_profile_jsons = [i for i in user_profile_jsons if not any(i["persona"] in p for p in generated_profiles)]
    for _id, user_profile_json in enumerate(tqdm.tqdm(user_profile_jsons, desc=f"Workflow {workflow_name}", total=len(user_profile_jsons))):
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
        simulated_results.append(simulated_res)
        fp.write(json.dumps(simulated_res, ensure_ascii=False)+"\n")
        fp.flush()
        
    # with open(ofn, "w") as f:
    #     json.dump(simulated_results, f, ensure_ascii=False, indent=4)
    #     print(f"Saved to {ofn}")
    return simulated_results

def run_simulations(base_cfg:Config, workflow_names, output_dir=_DIRECTORY_MANAGER.DIR_simulated_base/"tmp", max_workers=10):
    """ 
    args:
        conversation_dir: str, the directory of the conversation files
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for workflow_name in workflow_names:
            cfg = base_cfg.copy()
            cfg.workflow_name = workflow_name     # NOTE: update the config.workflow_name
            future = executor.submit(run_single_simulation, cfg, workflow_name, output_dir)
            futures.append(future)
        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Running simulations"):
            try:
                res_ = future.result()
            except Exception as e:
                print(f"[ERROR] for future: {future}\n{e}")
                for f in futures:
                    f.cancel()
                raise e


if __name__ == '__main__':
    # --- config overwrite ---
    
    cfg = Config.from_yaml(DataManager.normalize_config_name("simulate.yaml"))
    cfg.normalize_paths()       # fix the path
    
    VERSION = f"template={cfg.template_fn}_pdl={cfg.workflow_dir}_model={cfg.model_name}_api={cfg.api_mode}"
    VERSION = VERSION.replace("/", "_").replace(".", "_")
    odir = _DIRECTORY_MANAGER.DIR_simulated_base / VERSION
    
    # MODE = "single"
    MODE = "all"
    if MODE == "single":
        # --- run single ---
        workflow_name = "000-114挂号"
        # workflow_name = "001-注册邀约"
        # workflow_name = "002-新闻查询"
        cfg.workflow_name = workflow_name
        res = run_single_simulation(cfg, workflow_name, odir)
        print(f"simulated converstion: \n{res['simulated_conversation']}")
    elif MODE == "all":
        # --- run all ---
        # workflow_names = DataManager.get_workflow_name_list(_DIRECTORY_MANAGER.DIR_user_profile, extension=".json")
        workflow_names = ['000-114挂号', "002-新闻查询", '019-礼金礼卡类案件', '023-查号源日期', '025-酒店取消订单']  # '001-注册邀约', 
        print(f"workflow_names: {workflow_names}")

        max_workers = 50
        run_simulations(base_cfg=cfg, workflow_names=workflow_names, output_dir=odir, max_workers=max_workers)
    else:
        raise ValueError(f"Unknown MODE: {MODE}")
