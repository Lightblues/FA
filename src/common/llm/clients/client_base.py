from abc import abstractmethod
from typing import Dict, Iterator, List

from pydantic import BaseModel, Field


class BaseClient(BaseModel):
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.5)
    max_tokens: int = Field(default=4096)

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def query_one(self, query: str = None, messages: List[Dict] = None, **kwargs) -> str:
        """Simply query one response from the LLM"""
        pass

    @abstractmethod
    def query_one_stream(self, query: str = None, messages: List[Dict] = None, **args) -> Iterator[str]:
        """Query one response from the LLM, and stream the response"""
        pass
