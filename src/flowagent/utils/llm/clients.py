
import sys, os, json, re, time, requests, yaml, traceback
from typing import List, Dict, Optional, Tuple, Union, Iterator
import openai
from openai.types.chat import ChatCompletion
from tqdm import tqdm
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def stream_generator(response) -> Iterator[str]:
    for chunk in response:
        # yield chunk.choices[0].delta.content or ""
        text = chunk.choices[0].delta.content or ""
        text = text.replace("\n", "  \n")
        yield text


class OpenAIClient:
    base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o"
    client: openai.OpenAI = None
    temperature: float = 0.5
    max_tokens: int = 4096

    retries: int = 3
    backoff_factor: float = 0.5
    n_thread:int = 5
    
    is_sn: bool = False             # SN model | Deprecated

    def __init__(
        self, model_name:str=None, temperature:float=None, max_tokens:int=None,
        base_url=f"https://api.openai.com/v1", api_key=None, print_url=False, 
        is_sn:bool=None
    ):
        if not api_key:
            print(f"[WARNING] api_key is None, please set it in the environment variable (OPENAI_API_KEY) or pass it as a parameter.")
        if print_url:
            print(f"[INFO] base_url: {base_url}")
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        if model_name: self.model_name = model_name
        if temperature: self.temperature = temperature
        if max_tokens: self.max_tokens = max_tokens

    @staticmethod
    def _process_text_or_conv(query: str = None, messages: List[Dict] = None):
        if query is not None:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        elif messages is not None: pass
        else: raise ValueError("query or messages should be specified")
        return messages
    
    def _process_openai_args(self, args: Dict):
        if "model" not in args: args["model"] = self.model_name
        if "max_tokens" not in args: args["max_tokens"] = self.max_tokens
        if "temperature" not in args: args["temperature"] = self.temperature
        return args

    def query_one_raw(self, query: str = None, messages: List[Dict] = None, **args) -> ChatCompletion:
        messages = self._process_text_or_conv(query, messages)
        args = self._process_openai_args(args)
        chat_completion: ChatCompletion = self.client.chat.completions.create(messages=messages, **args)
        return chat_completion

    def query_one(
        self, 
        query: str = None, messages: List[Dict] = None, 
        return_model=False, return_usage=False, 
        **args
    ) -> Union[str, Tuple[str, ...]]:
        """ Get one response from OpenAI-fashion API
        Args:
            query or messages: input
            return_model, return_usage: control the output
        """
        messages = self._process_text_or_conv(query, messages)
        args = self._process_openai_args(args)
        # make query with retries
        for attempt in range(self.retries):
            try:
                chat_completion: ChatCompletion = self.client.chat.completions.create(messages=messages, **args)
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(self.backoff_factor * (2 ** attempt))
        else:
            raise Exception(f"Failed to get response after {self.retries} attempts.")
        # prepare the output
        if not return_model and not return_usage:
            return chat_completion.choices[0].message.content
        res = (chat_completion.choices[0].message.content, )
        if return_usage: return_model = True
        if return_model:
            res = res + (chat_completion.model, )
            if return_usage: res = res + (chat_completion.usage.to_dict(), )
        return res
    
    def query_one_stream_generator(self, text, stop=None) -> None:
        response = self.client.chat.completions.create(
            messages=[{ "role": "user", "content": text,}],
            model=self.model_name,
            temperature=self.temperature,
            stream=True,
            stop=stop
        )
        return stream_generator(response)
    
    def query_one_stream(self, text, stop=None, print_stream=True) -> None:
        res = ""
        stream = self.query_one_stream_generator(text, stop)
        for text in stream:
            res += text
            if print_stream:
                print(f"\033[90m{text}\033[0m", end="")
        if print_stream: print("\n")
        return res


    def query_many(self, texts, stop=None, temperature=None, model_id=None) -> list:
        with ThreadPoolExecutor(max_workers=self.n_thread) as executor:
            results = list(tqdm(executor.map(lambda x: self.query_one(x, stop, temperature, model_id), texts), total=len(texts), desc="Querying"))
        return results

    def embed_one(self, text:str) -> np.ndarray:
        text = text.replace("\n", " ")
        embedding_resp = None
        for attempt in range(self.retries):
            try:
                embedding_resp = self.client.embeddings.create(model=self.model_name, input=[text])
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(self.backoff_factor * (2 ** attempt))
        else:
            raise Exception(f"Failed to get response after {self.retries} attempts.")
        embedding = np.array(embedding_resp.data[0].embedding)
        return embedding

    def embed_batch(self, texts:list) -> np.ndarray:
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

