""" 
Usage::

    cd src/backend
    uvicorn main:app --host 0.0.0.0 --port 8100 --reload

@241208
- [x] basic implement with FastAPI

- [ ] mimic OpenAI stream API
    https://platform.openai.com/docs/api-reference/chat
    https://cookbook.openai.com/examples/how_to_stream_completions
"""
from fastapi import FastAPI
from pydantic import BaseModel

from .routers.single_agent import router as single_agent_router

app = FastAPI()

app.include_router(single_agent_router)


