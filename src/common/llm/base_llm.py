import importlib.util
import os
from typing import Dict, Union
from urllib.parse import urlparse

import yaml

from .clients.client_openai import OpenAIClient


LLM_CFG = {}


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
add_local_models()


def init_client(llm_cfg: Union[str, Dict]):
    if isinstance(llm_cfg, str):
        assert llm_cfg in LLM_CFG, f"{llm_cfg} not in LLM_CFG"
        return init_client(LLM_CFG[llm_cfg])
    # global client
    base_url = os.getenv("OPENAI_PROXY_BASE_URL") if llm_cfg.get("base_url") is None else llm_cfg["base_url"]
    api_key = os.getenv("OPENAI_PROXY_API_KEY") if llm_cfg.get("api_key") is None else llm_cfg["api_key"]
    model = llm_cfg.get("model", "gpt-4o")
    client = OpenAIClient(model=model, base_url=base_url, api_key=api_key)
    return client
