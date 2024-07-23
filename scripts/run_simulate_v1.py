""" 
@240716 并发模拟此前的 conversation, 保存到 $DATA/simulated 下
"""
import os, argparse, json
from tqdm import tqdm
import concurrent.futures
from simulator.simulator_v1 import SimulatorV1
from engine_v1.datamodel import Conversation
from engine_v1.common import DIR_conversation, DIR_data, DIR_simulated, DataManager, LLM_CFG, init_client


def run_single_simulation(workflow_name):
    """ Run simulation for a specific workflow
    input:
        workflow_name: str
        -> load workflow from $workflow_dir/$workflow_name
        -> load predetermined conversation from $workflow_dir/$workflow_name.json
    """
    global client
    
    # 0] Check if the simulation result exists
    ofn = f"{DIR_simulated}/{workflow_name}.json"
    if os.path.exists(ofn):
        print(f"[warning] {ofn} exists, skip")
        return
    
    simulated_results = []
    # 1] Load the LLM-generated conversation
    fn = f"{DIR_conversation}/{workflow_name}.json"
    with open(fn, "r") as f:
        ref_conversation_jsons = json.load(f)
    for ref_conversation_id, ref_conversation_json in enumerate(ref_conversation_jsons):
        ref_conversation = Conversation.load_from_json(ref_conversation_json)
        
        # 2] Initialize the simulator
        simulator = SimulatorV1(client=client, workflow_dir=DIR_data)                 # NOTE: simulator's PDL must be in line with ref_conversation!!!

        # 3] Run the simulation with the ref_conversation
        infos, conversation = simulator.simulate(workflow_name, ref_conversation)
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

def run_simulations(max_workers=10, conversation_dir=DIR_conversation):
    workflow_names = DataManager.get_workflow_name_list(conversation_dir, extension=".json")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for workflow_name in workflow_names:
            future = executor.submit(run_single_simulation, workflow_name)
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
    model_name = "qwen2_72B"
    client = init_client(llm_cfg=LLM_CFG[model_name])
    
    max_workers = 10
    run_simulations(max_workers=max_workers, conversation_dir=DIR_conversation)
