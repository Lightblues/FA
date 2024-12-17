"""
Usage::

    cd src
    uvicorn api_server.main:app --host 0.0.0.0 --port 9390 --reload --reload-dir ./api_server

1. 设计API schema (definitions)
2. 模拟调用, 这里直接 mock 了
3. 整理API调用形式 (openapi.json), 转换为可解析的形式
"""

import pathlib

import yaml  # 或者 json, toml 等
from fastapi import FastAPI

from .api_definitions import *  # NOTE: to register the apis
from .api_registry import api_registry
from .mocker import Mocker


DIR = pathlib.Path(__file__).parent


def register_apis(app: FastAPI, config: dict):
    # 动态创建路由
    mocker = Mocker(model_name=config["model_name"])
    for api_name, api_info in api_registry.registry.items():
        route = app.post(f"/{api_name}")(mocker.create_dynamic_api(api_name, api_info))
    return app


def load_config():
    with open(DIR / "config.yaml", "r") as f:
        return yaml.safe_load(f)


config = load_config()
app = FastAPI()
register_apis(app, config)
