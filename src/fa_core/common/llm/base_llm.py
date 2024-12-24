import importlib.util
import os
from typing import Dict, Union
from urllib.parse import urlparse

import yaml

from .clients.client_openai import OpenAIClient
from .clients.client_hunyuan import HunyuanClient

LLM_CFG = {}  # Link llm_name -> base_url, api_key, model

HUNYUAN_MODEL_LIST = [
    "hunyuan-turbo",
    "hunyuan-large",
    "hunyuan-pro",
    "hunyuan-standard",
    "hunyuan-standard-256K",
    "hunyuan-lite",
    "hunyuan-turbo-latest",
    "hunyuan-large-longcontext",
    "hunyuan-turbo-vision",
    "hunyuan-vision",
    "hunyuan-code",
    "hunyuan-role",
    "hunyuan-functioncall",
]


def add_openai_models():
    global LLM_CFG

    if os.getenv("OPENAI_PROXY_BASE_URL", None) is not None:
        model_list = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-4",
            "claude-3-haiku-20240307",
            # "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
        ]
        for model in model_list:
            LLM_CFG[model] = {
                "model": model,
                "base_url": os.getenv("OPENAI_PROXY_BASE_URL"),
                "api_key": os.getenv("OPENAI_PROXY_API_KEY"),
            }

    if os.getenv("SILICONFLOW_BASE_URL", None) is not None:
        model_list = [
            "Vendor-A/Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-72B-Instruct-128K",
        ]
        for model in model_list:
            LLM_CFG[model] = {
                "model": model,
                "base_url": os.getenv("SILICONFLOW_BASE_URL"),
                "api_key": os.getenv("SILICONFLOW_API_KEY"),
            }


def add_hunyuan_models():
    global LLM_CFG

    for model in HUNYUAN_MODEL_LIST:
        LLM_CFG[model] = {"model": model}


def add_local_models():
    global LLM_CFG

    fn_local_models_config = os.getenv("LOCAL_MODELS_CONFIG_PATH", None)
    if (fn_local_models_config is not None) and (os.path.exists(fn_local_models_config)):
        with open(fn_local_models_config, "r") as f:
            LLM_CFG |= yaml.load(f, Loader=yaml.FullLoader)

    fn_local_models_info = os.getenv("LOCAL_MODELS_INFO_PATH", None)
    if (fn_local_models_info is not None) and (os.path.exists(fn_local_models_info)):
        spec = importlib.util.spec_from_file_location("model_urls", fn_local_models_info)
        model_urls = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(model_urls)
        model_info = {}
        for name, url in model_urls.local_urls.items():  # process the `local_urls` object
            if "http" not in url:
                continue
            parsed_url = urlparse(url)
            model_info[name] = f"{parsed_url.scheme}://{parsed_url.netloc}"
        for model, url in model_info.items():
            # assert model not in LLM_CFG, f"{model} already in LLM_CFG"
            if model in LLM_CFG:
                print(f"[warning] <add_local_models> {model} already exist! pass!")
                continue
            LLM_CFG[model] = {
                "model": model,
                "base_url": url,
                "api_key": "xxx",  # NOTE: api_key 不能为 "" 不然也会报错
            }


add_openai_models()
add_hunyuan_models()
add_local_models()


def init_client(model: str, **kwargs):
    """Initialize the LLM client

    Args:
        model: the configed model name
        **kwargs: the kwargs for LLM
    """
    if model in HUNYUAN_MODEL_LIST:
        return HunyuanClient(kwargs={"model": model, **kwargs})

    assert model in LLM_CFG, f"{model} not in LLM_CFG"
    client = OpenAIClient(
        base_url=LLM_CFG[model].get("base_url", os.getenv("OPENAI_PROXY_BASE_URL")),
        api_key=LLM_CFG[model].get("api_key", os.getenv("OPENAI_PROXY_API_KEY")),
        kwargs={"model": LLM_CFG[model].get("model", "gpt-4o"), **kwargs},
    )
    return client
