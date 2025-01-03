from abc import abstractmethod
from typing import Dict, Iterator, List

from pydantic import BaseModel, Field, ConfigDict


class BaseClient(BaseModel):
    kwargs: Dict = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)  # for openai.OpenAI

    @abstractmethod
    def query_one(self, query: str = None, messages: List[Dict] = None, **kwargs) -> str:
        """Simply query one response from the LLM"""
        pass

    @abstractmethod
    def query_one_stream(self, query: str = None, messages: List[Dict] = None, **args) -> Iterator[str]:
        """Query one response from the LLM, and stream the response"""
        pass

    @property
    def model_name(self):
        return self.kwargs["model"]
