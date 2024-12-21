"""@241219
doc: https://cloud.tencent.com/document/api/1729/105701
"""

import json
import os
from typing import Dict, Iterator, List, Optional

from loguru import logger
from pydantic import BaseModel, Field
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile, RegionBreakerProfile
from tencentcloud.hunyuan.v20230901.hunyuan_client import HunyuanClient as _HunyuanClient
from tencentcloud.hunyuan.v20230901.models import ChatCompletionsRequest, ChatCompletionsResponse

from .client_base import BaseClient


def get_hunyuan_client() -> _HunyuanClient:
    # 1. setup credentials
    secret_id, secret_key = (
        os.environ.get("TENCENTCLOUD_SECRET_ID", ""),
        os.environ.get("TENCENTCLOUD_SECRET_KEY", ""),
    )
    if not secret_id or not secret_key:
        logger.warning("TENCENTCLOUD_SECRET_ID or TENCENTCLOUD_SECRET_KEY not set, using default credentials!")
        secret_id, secret_key = "xxx", "xxx"
    cred = credential.Credential(secret_id, secret_key)
    # 2. setup profile
    profile = ClientProfile(
        region_breaker_profile=RegionBreakerProfile(
            max_fail_num=5,
            max_fail_percent=0.75,
            window_interval=60 * 5,
            timeout=60 * 5,  # 60, addup the timeout to 5 minutes
            max_requests=5,
        )
    )
    return _HunyuanClient(credential=cred, region="ap-beijing", profile=profile)


# https://cloud.tencent.com/document/api/1729/105701#2.-.E8.BE.93.E5.85.A5.E5.8F.82.E6.95.B0
HUNYUAN_DEFAULT_CONFIG = {
    "model": "hunyuan-turbo",
    "messages": [],  # NOTE Role & Content
    "stream": False,
    "top_p": None,
    "temperature": None,
    "enable_enhancement": False,
    "stop": [],
    "tools": [],
    "tool_choice": None,  # "auto" or "none" or "custom"
}


class HunyuanClient(BaseClient):
    kwargs: Dict = Field(default_factory=dict)

    client: Optional[_HunyuanClient] = None

    def model_post_init(self, *args, **kwargs):
        self.client = get_hunyuan_client()

        if set(self.kwargs.keys()) - set(HUNYUAN_DEFAULT_CONFIG.keys()):
            logger.warning(f"WARNING: {set(self.kwargs.keys()) - set(HUNYUAN_DEFAULT_CONFIG.keys())} are not supported by Hunyuan API")
        self.kwargs = {**HUNYUAN_DEFAULT_CONFIG, **self.kwargs}

    def _process_text_or_conv(self, query: str = None, messages: List[Dict] = None):
        if query:
            messages = [{"Role": "system", "Content": "You are a helpful assistant."}, {"Role": "user", "Content": query}]
        else:
            assert messages is not None, "query or messages should be specified"
        return messages

    def _process_hunyuan_kwargs(self, kwargs: Dict) -> ChatCompletionsRequest:
        req = ChatCompletionsRequest()
        if "query" in kwargs and kwargs["query"]:
            if "messages" in kwargs and kwargs["messages"]:
                raise ValueError("query and messages should not be specified at the same time")
            kwargs["messages"] = self._process_text_or_conv(kwargs["query"])
        else:
            assert "messages" in kwargs and kwargs["messages"], "messages should be specified"
        req.Messages = kwargs["messages"]
        req.Model = kwargs.get("model", self.kwargs["model"])
        req.TopP = kwargs.get("top_p", self.kwargs["top_p"])
        req.Temperature = kwargs.get("temperature", self.kwargs["temperature"])
        req.Stop = kwargs.get("stop", self.kwargs["stop"])
        req.Stream = kwargs.get("stream", self.kwargs["stream"])
        req._EnableEnhancement = kwargs.get("enable_enhancement", self.kwargs["enable_enhancement"])
        if kwargs.get("tools") and kwargs["tools"]:
            req.CustomTool = kwargs["tools"]
            req.ToolChoice = kwargs.get("tool_choice", self.kwargs["tool_choice"])
        return req

    # -----------------------------------------------------------------------------------------------------------
    def chat_completions(self, **kwargs) -> ChatCompletionsResponse:
        kwargs = self._process_hunyuan_kwargs(kwargs)
        return self.client.ChatCompletions(kwargs)

    # -----------------------------------------------------------------------------------------------------------
    def query_one(self, query: str = None, messages: List[Dict] = None, **kwargs) -> str:
        response = self.chat_completions(query=query, messages=messages, **kwargs)
        return response.Choices[0].Message.Content

    def query_one_stream(self, query: str = None, messages: List[Dict] = None, **kwargs) -> Iterator[str]:
        kwargs["stream"] = True  # NOTE: set stream=True in kwargs
        response = self.chat_completions(query=query, messages=messages, **kwargs)
        return self.stream_generator(response)

    def stream_generator(self, response: Dict) -> Iterator[str]:
        for chunk in response:
            data = json.loads(chunk["data"])
            yield data["Choices"][0]["Delta"]["Content"]
