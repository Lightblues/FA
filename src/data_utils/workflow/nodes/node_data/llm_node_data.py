from pydantic import BaseModel
from typing import *
from .base import NodeDataBase

class LLMNodeData(NodeDataBase):
    ModelName: str
    Temperature: float
    TopP: float
    MaxTokens: int
    Prompt: str

    def __str__(self):
        return f"[LLM] {self.ModelName} {self.Prompt[:15]}..."