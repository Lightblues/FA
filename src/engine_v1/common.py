import os, sys, time, datetime
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater

DIR_data = "../data/v240628/huabu_step3"
DIR_log = "../data/engine_v1_log"

LLM_stop = ["[USER]"]

API_base_rul = "http://localhost:8000"
API_infos = [ 
    {
        "name": "通过交易金额查询",
        "endpoint": "/query_by_amount", 
        "request": ["amount"],
        "response": ["order_links"],
        "request_zh": ["交易金额"],
        "response_zh": ["订单编号超链"],
    },
    {
        "name": "通过交易时间查询",
        "endpoint": "/query_by_time",
        "request": ["transaction_time"],
        "response": ["order_links"],
        "request_zh": ["交易时间"],
        "response_zh": ["订单编号超链"],
    },
    {
        "name": "通过订单编号查询",
        "endpoint": "/query_by_order_id",
        "request": ["order_id"],
        "response": ["details"],
        "request_zh": ["订单编号"],
        "response_zh": ["订单详情"],
    },
]

def init_client(llm_cfg:Dict):
    # global client
    base_url = os.getenv("OPENAI_PROXY_BASE_URL") if llm_cfg.get("base_url") is None else llm_cfg["base_url"]
    api_key = os.getenv("OPENAI_PROXY_API_KEY") if llm_cfg.get("api_key") is None else llm_cfg["api_key"]
    model_name = llm_cfg.get("model_name", "gpt-4o")
    client = OpenAIClient(
        model_name=model_name, base_url=base_url, api_key=api_key
    )
    return client