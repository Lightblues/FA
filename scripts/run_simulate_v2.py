""" 
@240723 并发模拟此前的 conversation, 保存到 $DATA/simulated 下
"""
import os, argparse, json
from tqdm import tqdm
import concurrent.futures
from simulator.simulator_v2 import SimulatorV2
from engine_v2.datamodel import Conversation, Config
from engine_v2.common import DIR_conversation_v1, DIR_huabu_step3, DIR_simulated_base, DataManager, LLM_CFG, init_client


def run_single_simulation(cfg:Config, workflow_name:str, odir:str=DIR_simulated_base/"tmp"):
    """ Run simulation for a specific workflow
    input:
        workflow_name: str
        -> load workflow from $workflow_dir/$workflow_name
        -> load predetermined conversation from $workflow_dir/$workflow_name.json
    """
    # 0] Check if the simulation result exists
    os.makedirs(odir, exist_ok=True)
    ofn = f"{odir}/{workflow_name}.json"
    if os.path.exists(ofn):
        print(f"[warning] {ofn} exists, skip")
        return
    
    assert cfg.workflow_name == workflow_name, f"{cfg.workflow_name} != {workflow_name}"
    simulated_results = []
    # 1] Load the LLM-generated conversation
    fn = f"{DIR_conversation_v1}/{workflow_name}.json"
    with open(fn, "r") as f:
        ref_conversation_jsons = json.load(f)
    for ref_conversation_id, ref_conversation_json in enumerate(ref_conversation_jsons):
        ref_conversation = Conversation.load_from_json(ref_conversation_json)
        
        # 2] Initialize the simulator
        simulator = SimulatorV2(cfg)

        # 3] Run the simulation with the ref_conversation
        infos, conversation = simulator.start_simulation(ref_conversation)
        simulated_results.append({
            "workflow_name": workflow_name,
            "ref_conversation": ref_conversation.to_str(),
            "simulated_conversation": conversation.to_str(),
            "meta_infos": infos,
        })
    with open(ofn, "w") as f:
        json.dump(simulated_results, f, ensure_ascii=False, indent=4)
        print(f"Saved to {ofn}")
    return simulated_results

def run_simulations(base_cfg:Config, conversation_dir=DIR_conversation_v1, output_dir=DIR_simulated_base/"tmp", max_workers=10):
    """ 
    args:
        conversation_dir: str, the directory of the conversation files
    """
    workflow_names = DataManager.get_workflow_name_list(conversation_dir, extension=".json")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for workflow_name in workflow_names:
            cfg = base_cfg.copy()
            cfg.workflow_name = workflow_name     # NOTE: update the config.workflow_name
            future = executor.submit(run_single_simulation, cfg, workflow_name, output_dir)
            futures.append(future)
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            try:
                res_ = future.result()
            except Exception as e:
                print(f"[ERROR] for future: {future}\n{e}")
                for f in futures:
                    f.cancel()
                raise e


if __name__ == '__main__':
    # --- config overwrite ---
    workflow_dir = "huabu_step3"
    template_fn =  "query_PDL_v04.jinja"
    
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    cfg.workflow_dir = workflow_dir
    cfg.template_fn = template_fn
    cfg.model_name = "qwen2_72B"
    cfg.api_mode = "v01"
    cfg.api_model_name = "gpt-4o-mini"
    cfg.normalize_paths()       # fix the path
    
    VERSION = f"template={template_fn}_pdl={workflow_dir}_model={cfg.model_name}_api={cfg.api_mode}"
    VERSION = VERSION.replace("/", "_").replace(".", "_")
    odir = DIR_simulated_base / VERSION
    
    MODE = "single"
    MODE = "all"
    if MODE == "single":
        # --- run single ---
        workflow_name = "000-114挂号"
        # workflow_name = "001-注册邀约"
        # workflow_name = "002-新闻查询"
        cfg.workflow_name = workflow_name
        run_single_simulation(cfg, workflow_name, odir)
    elif MODE == "all":
        # --- run all ---
        max_workers = 10
        run_simulations(base_cfg=cfg, conversation_dir=DIR_conversation_v1, output_dir=odir, max_workers=max_workers, )
    else:
        raise ValueError(f"Unknown MODE: {MODE}")
