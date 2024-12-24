from abc import abstractmethod
from typing import Dict, Iterator, List

from pydantic import BaseModel, Field


class BaseClient(BaseModel):
    kwargs: Dict = Field(default_factory=dict)

    @property
    def model(self):
        return self.kwargs.get("model", "gpt-4o")

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
