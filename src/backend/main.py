""" 
Usage::

    cd src/backend
    uvicorn main:app --host 0.0.0.0 --port 8100 --reload

@241208
- [x] basic implement with FastAPI
@241209
- [x] mimic OpenAI stream API
    https://platform.openai.com/docs/api-reference/chat
    https://cookbook.openai.com/examples/how_to_stream_completions
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from flowagent.data import Config

from .common.shared import SharedResources


def init_app() -> FastAPI:
    # Initialize configuration
    cfg = Config()
    SharedResources.initialize(cfg)

    app = FastAPI(
        title="FlowAgent API",
        description="Backend API for FlowAgent",
        version="0.1.0",
        lifespan=lifespan,
    )
    return app

def setup_router(app: FastAPI):
    from .routers.router_single_agent import router_single
    app.include_router(router_single)
    return app


# NOTE: @app.on_event("shutdown") is deprecated!
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down...")

    from .routers.router_single_agent import clear_session_contexts
    clear_session_contexts()

app = init_app()
setup_router(app)


