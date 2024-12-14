from pydantic import BaseModel
from typing import *
from .base import NodeDataBase

class AnswerNodeData(NodeDataBase):
    """Answer node data"""
    Answer: str

    def __str__(self):
        return f"[Answer] {self.Answer[:15]}..."
