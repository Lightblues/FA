"""
Usage::

    cd src
    CONFIG_NAME=default.yaml uvicorn backend.main:app --host 0.0.0.0 --port 8100 --reload --reload-dir ./backend

@241208
- [x] basic implement with FastAPI
@241209
- [x] mimic OpenAI stream API
    https://platform.openai.com/docs/api-reference/chat
    https://cookbook.openai.com/examples/how_to_stream_completions
@241211
- [x] #feat add the `lifespan` feature with `asynccontextmanager`
- [x] #structure seperate the `setup_router()`
@241212
- [x] #feat set `--reload_dir ./backend` for `uvicorn`
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from common import Config, init_loguru_logger
from flowagent.data import DataManager

from .common.shared import SharedResources


def init_app() -> FastAPI:
    # Get config name from environment variable, default to 'default.yaml'
    config_name = os.environ.get("CONFIG_NAME", "default.yaml")

    # Initialize configuration
    cfg = Config.from_yaml(config_name)
    init_loguru_logger(DataManager.DIR_backend_log)
    SharedResources.initialize(cfg)

    app = FastAPI(
        title="FlowAgent API",
        description="Backend API for FlowAgent",
        version="0.1.0",
        lifespan=lifespan,
    )
    return app


def setup_router(app: FastAPI):
    from .routers.router_multi import router_multi
    from .routers.router_single import router_single
    from .routers.router_tool import router_tool

    app.include_router(router_single)  # add the prefix `/single`?
    app.include_router(router_multi)
    app.include_router(router_tool)
    return app


# NOTE: @app.on_event("shutdown") is deprecated!
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down...")

    from .routers.session_context_multi import clear_session_contexts_multi
    from .routers.session_context_single import clear_session_contexts_single

    clear_session_contexts_single()
    clear_session_contexts_multi()
    print("Cleanup completed")


app = init_app()
setup_router(app)
