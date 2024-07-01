import os, sys, time, datetime
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater

DIR_data = "../data/v240628/huabu_step3"
DIR_log = "../data/engine_v1_log"

def init_client(llm_cfg:Dict):
    # global client
    base_url = os.getenv("OPENAI_PROXY_BASE_URL") if llm_cfg.get("base_url") is None else llm_cfg["base_url"]
    api_key = os.getenv("OPENAI_PROXY_API_KEY") if llm_cfg.get("api_key") is None else llm_cfg["api_key"]
    model_name = llm_cfg.get("model_name", "gpt-4o")
    client = OpenAIClient(
        model_name=model_name, base_url=base_url, api_key=api_key
    )
    return client