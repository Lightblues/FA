import json
import random
import argparse
import pandas as pd

from data_creater import ProfileCreater
from engine import Config, BaseRole, DataManager, DIR_conversation

DATA_DIR = '/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/data'
HUABU_DIR = '/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/jobs/huabu_test/huabu'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="gpt-4o-mini")
    parser.add_argument("--random_seed", type=int, default=42)
    parser.add_argument("--sample_number", type=int, default=50)
    args = parser.parse_args()
    cfg = Config()
    cfg.model_name = args.model_name
    # profile creater
    creater = ProfileCreater(cfg=cfg)
    
    # load workflow
    workflow_id_map = DataManager.build_workflow_id_map(DIR_conversation, extension=".json")
    # print(workflow_id_map)
    workflow_list = sorted(list(set(workflow_id_map.values())))
    task_desc = {}
    with open('/apdcephfs_cq8/share_2992827/shennong_5/siqiicai/jobs/huabu_test/huabu/data/gen/meta/data_meta.json', 'r', encoding='utf-8') as f:
        task_meta = json.load(f)
        for i, task_info in enumerate(task_meta):
            task_name = task_info['PDL_name']
            # print('task name:', task_name)
            curr_workflow = workflow_list[i]
            task_desc[curr_workflow] = f"{task_info['PDL_description']}。任务流程：{task_info['PDL_detailed_description']}"

    # load personas
    # persona_df = pd.read_csv(f'{DATA_DIR}/persona-hub/persona_sampled.csv')
    # personas = persona_df['persona'].tolist()
    with open(f'{DATA_DIR}/persona-hub/persona_expanded.jsonl', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        personas = [json.loads(line.strip())['persona'] for line in lines]
    print(workflow_list)
    print(task_desc.keys())
    # print(personas)
    
    task_profile = {}
    for workflow in workflow_list:
        # sample 50 of all the personas for each task
        print(task_desc[workflow])
        curr_personas = random.sample(personas, args.sample_number)
        profiles = creater.create_profile(workflow, curr_personas, task_desc=task_desc[workflow])
        task_profile[workflow] = profiles
    
        with open(f"{HUABU_DIR}/data/gen/user_profile_expanded/{workflow}.json", 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
