"""
- [ ] add tool calling
"""

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
import openai
from loguru import logger
from openai._streaming import Stream
from openai.lib._parsing import ResponseFormatT
from openai.resources.beta.chat.completions import ChatCompletionStreamManager
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from pydantic import BaseModel, Field
from tqdm import tqdm

from .client_base import BaseClient


class OpenAIClient(BaseClient):
    base_url: str = Field(default="https://api.openai.com/v1")
    api_key: Optional[str] = None

    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.5)
    max_tokens: int = Field(default=4096)
    stream: bool = Field(default=False)

    retries: int = Field(default=3)
    backoff_factor: float = Field(default=0.5)
    n_thread: int = Field(default=5)
    is_sn: bool = Field(default=False)  # SN model | Deprecated

    client: Optional[openai.OpenAI] = None

    def model_post_init(self, *args, **kwargs):
        if not self.api_key:
            logger.warning(f"[WARNING] api_key is None, please set it in the environment variable (OPENAI_API_KEY) or pass it as a parameter.")
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    # -----------------------------------------------------------------------------------------------------------
    def chat_completions_create(self, *args, **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]:
        return self.client.chat.completions.create(*args, **kwargs)

    def beta_chat_completions_stream(self, *args, **kwargs) -> ChatCompletionStreamManager[ResponseFormatT]:
        return self.client.beta.chat.completions.stream(*args, **kwargs)

    # -----------------------------------------------------------------------------------------------------------
    def _process_text_or_conv(self, query: str = None, messages: List[Dict] = None):
        if query:
            messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": query}]
        else:
            assert messages is not None, "query or messages should be specified"
        return messages

    def _query_openai(self, messages: List[Dict], **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]:
        req = {
            # TODO: align more args
            "messages": messages,
            "model": kwargs.get("model", self.model),
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": kwargs.get("stream", self.stream),
        }
        return self.client.chat.completions.create(**req)

    def query_one_raw(self, query: str = None, messages: List[Dict] = None, **kwargs) -> ChatCompletion:
        messages = self._process_text_or_conv(query, messages)
        chat_completion: ChatCompletion = self._query_openai(messages, **kwargs)
        return chat_completion

    def query_one(
        self, query: str = None, messages: List[Dict] = None, return_model=False, return_usage=False, **kwargs
    ) -> Union[str, Tuple[str, ...]]:
        """Get one response from OpenAI-fashion API
        Args:
            query or messages: input
            return_model, return_usage: control the output
        """
        messages = self._process_text_or_conv(query, messages)
        # make query with retries
        for attempt in range(self.retries):
            try:
                chat_completion: ChatCompletion = self._query_openai(messages, **kwargs)
                break
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(self.backoff_factor * (2**attempt))
        else:
            raise Exception(f"Failed to get response after {self.retries} attempts.")
        # prepare the output
        if not return_model and not return_usage:
            return chat_completion.choices[0].message.content
        res = (chat_completion.choices[0].message.content,)
        if return_usage:
            return_model = True
        if return_model:
            res = res + (chat_completion.model,)
            if return_usage:
                res = res + (chat_completion.usage.to_dict(),)
        return res

    def query_one_stream(self, query: str = None, messages: List[Dict] = None, **kwargs) -> Iterator[str]:
        messages = self._process_text_or_conv(query, messages)
        kwargs["stream"] = True
        response = self._query_openai(messages, **kwargs)

        def stream_generator(response) -> Iterator[str]:
            for chunk in response:
                yield chunk.choices[0].delta.content or ""

        return stream_generator(response)

    def query_many(self, texts, stop=None, temperature=None, model_id=None) -> list:
        with ThreadPoolExecutor(max_workers=self.n_thread) as executor:
            results = list(tqdm(executor.map(lambda x: self.query_one(x, stop, temperature, model_id), texts), total=len(texts), desc="Querying"))
        return results

    # -----------------------------------------------------------------------------------------------------------
    def embed_one(self, text: str) -> np.ndarray:
        text = text.replace("\n", " ")
        embedding_resp = None
        for attempt in range(self.retries):
            try:
                embedding_resp = self.client.embeddings.create(model=self.model, input=[text])
                break
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(self.backoff_factor * (2**attempt))
        else:
            raise Exception(f"Failed to get response after {self.retries} attempts.")
        embedding = np.array(embedding_resp.data[0].embedding)
        return embedding

    def embed_batch(self, texts: list) -> np.ndarray:
        """
        Embed a batch of texts based on OpenAI API.

        Args:
            texts: list of texts to embed

        Returns:
            embeddings of the texts
        """
        with ThreadPoolExecutor(max_workers=self.n_thread) as executor:
            results = list(tqdm(executor.map(lambda x: self.embed_one(x), texts), total=len(texts), desc="Querying"))
        return np.array(results)
