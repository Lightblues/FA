"""@241219
doc: https://cloud.tencent.com/document/api/1729/105701
"""

import json
import os
from typing import Dict, Iterator, List, Optional

from loguru import logger
from pydantic import BaseModel, Field
from tencentcloud.common import credential
from tencentcloud.hunyuan.v20230901.hunyuan_client import HunyuanClient as _HunyuanClient
from tencentcloud.hunyuan.v20230901.models import ChatCompletionsRequest, ChatCompletionsResponse

from .client_base import BaseClient


def get_hunyuan_client() -> _HunyuanClient:
    secret_id, secret_key = (
        os.environ.get("TENCENTCLOUD_SECRET_ID", ""),
        os.environ.get("TENCENTCLOUD_SECRET_KEY", ""),
    )
    if not secret_id or not secret_key:
        logger.warning("TENCENTCLOUD_SECRET_ID or TENCENTCLOUD_SECRET_KEY not set, using default credentials!")
        secret_id, secret_key = "xxx", "xxx"
    cred = credential.Credential(secret_id, secret_key)
    return _HunyuanClient(cred, "ap-beijing")


class HunyuanClient(BaseClient):
    # args: https://cloud.tencent.com/document/api/1729/105701#2.-.E8.BE.93.E5.85.A5.E5.8F.82.E6.95.B0
    model: str = Field(default="hunyuan-turbo")
    temperature: float = Field(default=0.5)
    top_p: float = Field(default=1)
    stop: List[str] = Field(default=[])

    enable_enhancement: bool = Field(default=False)  # NOTE: whether to use search enhancement
    stream: bool = Field(default=False)

    client: Optional[_HunyuanClient] = None

    def model_post_init(self, *args, **kwargs):
        self.client = get_hunyuan_client()

    # def _process_hy_args(self, args: Dict):
    #     if "model" not in args: args["model"] = self.model
    #     if "temperature" not in args: args["temperature"] = self.temperature
    #     if "top_p" not in args: args["top_p"] = self.top_p
    #     if "stop" not in args: args["stop"] = self.stop
    #     return args

    def _process_text_or_conv(self, query: str = None, messages: List[Dict] = None):
        if query:
            messages = [{"Role": "system", "Content": "You are a helpful assistant."}, {"Role": "user", "Content": query}]
        else:
            assert messages is not None, "query or messages should be specified"
        return messages

    def _query_hy(self, messages: List[Dict], **kwargs):
        req = ChatCompletionsRequest()
        req._Messages = messages
        req._Model = kwargs.get("model", self.model)
        req._TopP = kwargs.get("top_p", self.top_p)
        req._Temperature = kwargs.get("temperature", self.temperature)
        req._Stop = kwargs.get("stop", self.stop)
        req._Stream = kwargs.get("stream", self.stream)
        req._EnableEnhancement = kwargs.get("enable_enhancement", self.enable_enhancement)
        return self.client.ChatCompletions(req)

    def query_one(self, query: str = None, messages: List[Dict] = None, **kwargs) -> str:
        messages = self._process_text_or_conv(query, messages)
        response = self._query_hy(messages, **kwargs)
        return response.Choices[0].Message.Content

    def query_one_stream(self, query: str = None, messages: List[Dict] = None, **kwargs) -> Iterator[str]:
        messages = self._process_text_or_conv(query, messages)
        kwargs["stream"] = True  # NOTE: set stream=True in kwargs
        response = self._query_hy(messages, **kwargs)

        def stream_generator(response: Dict) -> Iterator[str]:
            for chunk in response:
                data = json.loads(chunk["data"])
                yield data["Choices"][0]["Delta"]["Content"]

        return stream_generator(response)
