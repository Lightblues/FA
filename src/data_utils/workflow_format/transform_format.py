import re
import os
import time
from tqdm import tqdm
import json
import datetime
import argparse
from typing import Optional, List
from tabulate import tabulate

from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater
from .format_transformer import FormatTransformer, APITransformer


def transform_api_format(args):
    API_transformer = APITransformer(args.model_name, "transform_api_format.jinja")
    
    tasks = os.listdir(f"{args.dataset_dir}/{args.api_path}")
    tasks = [task.split('.')[0] for task in tasks if '.' in task]
    for task in tasks:
        # 加载并将原始API转化成标准形式
        with open(f"{args.dataset_dir}/{args.api_path}/{task}.json", 'r', encoding='utf-8') as f:
            curr_api = json.load(f)
            transformed_api = API_transformer.transform(api=curr_api)
        # 写入转化结果
        with open(f"{args.dataset_dir}/{args.transformed_api_path}/{task}.json", 'w', encoding='utf-8') as f:
            json.dump(transformed_api, f, indent=2)
        

format_to_codeblock = {
    "PDL": "PDL",
    "code": "python",
    "CoRE": "CoRE",
    "flowchart": "mermaid"
}
def transform_NL_to_other_format(args, target_format):
    NL_transformer = FormatTransformer(args.model_name, f"NL_to_{target_format}.jinja", return_format=format_to_codeblock[target_format])
    # 获取任务列表
    tasks = os.listdir(f"{args.dataset_dir}/{args.workflow_path}")
    tasks = [task.split('.')[0] for task in tasks if '.' in task]
    for task in tqdm(tasks):
        # 加载任务的自然语言描述以及可用的API
        with open(f"{args.dataset_dir}/{args.transformed_workflow_path}/NL/{task}.json", 'r', encoding='utf-8') as f:
            task_desc = json.load(f)
        with open(f"{args.dataset_dir}/{args.transformed_api_path}/{task}.json", 'w', encoding='utf-8') as f:
            apis = json.load(f)
            
        # 转化成目标格式
        transformed_workflow = NL_transformer.transform(NL_desc=task_desc, apis=apis)
        file_suffix = "txt" if target_format != "code" else "py"
        with open(f"{args.dataset_dir}/{args.transformed_workflow_path}/{target_format}/{task}.{file_suffix}", 'w', encoding='utf-8') as f:
            f.write(transformed_workflow)
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_dir", type=str, default="/apdcephfs/share_2992827/shennong_5/siqiicai/data/STAR")
    parser.add_argument("--workflow_path", type=str, default="tasks")
    parser.add_argument("--transformed_workflow_path", type=str, default="tasks_transformed")
    parser.add_argument("--api_path", type=str, default="apis")
    parser.add_argument("--transformed_api_path", type=str, default="apis/apis_transformed")
    parser.add_argument("--model_name", type=str, default="gpt-4o")
    parser.add_argument("--target_formats", type=str, default="PDL,code,CoRE,flowchart")
    args = parser.parse_args()
    
    target_formats = args.target_formats.split(',')
    for target_format in target_formats:
        transform_NL_to_other_format(args, target_format)
