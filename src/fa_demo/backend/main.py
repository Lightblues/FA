"""
Usage::

    # Method 1: Run with uvicorn directly
    cd src
    CONFIG_NAME=default.yaml uvicorn fa_demo.backend.main:app --host 0.0.0.0 --port 8100 --reload --reload-dir ./fa_demo/backend

    # Method 2: Run with python script
    cd src
    python run_demo_backend.py --config=default.yaml
    python run_demo_backend.py --config=default.yaml --port=8100 --reload

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

from fa_core.common import Config, init_loguru_logger
from fa_core.data import FADataManager

from .common.shared import SharedResources


def init_app(config_name: str | None = None) -> FastAPI:
    """Initialize FastAPI application

    Args:
        config_name: Optional config file name. If None, will try to get from environment variable
    """
    # Get config name from parameter or environment variable
    config_name = config_name or os.environ.get("CONFIG_NAME", "default.yaml")

    # Initialize configuration
    print(f"Backend loading config: {config_name}")
    cfg = Config.from_yaml(config_name)
    init_loguru_logger(FADataManager.DIR_backend_log)
    SharedResources.initialize(cfg)

    app = FastAPI(
        title="FlowAgent API",
        description="Backend API for FlowAgent",
        version="0.1.0",
        lifespan=lifespan,
    )
    return app


def setup_router(app: FastAPI):
    from .routers.router_inspect import router_inspect
    from .routers.router_multi import router_multi
    from .routers.router_single import router_single
    from .routers.router_tool import router_tool

    app.include_router(router_inspect)
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


# Create a function that returns the app instance with config
def create_app(config_name: str) -> FastAPI:
    """Create FastAPI application with specific config"""
    app = init_app(config_name)
    setup_router(app)
    return app


# For direct usage with uvicorn (environment variable based)
app = init_app()
setup_router(app)
