"""
from @ian /cq8/ianxxu/chatchat/_TaskPlan/UI/v2.1/tools/hunyuan_search.py
https://github.com/TencentCloud/tencentcloud-sdk-python/blob/master/tencentcloud/hunyuan/v20230901/models.py

pip install --upgrade tencentcloud-sdk-python
"""

import json
import os
from typing import Iterator

from loguru import logger
from tencentcloud.common import credential
from tencentcloud.hunyuan.v20230901.hunyuan_client import HunyuanClient
from tencentcloud.hunyuan.v20230901.models import (
    ChatCompletionsRequest,
)

from .register import register_tool


secret_id, secret_key = (
    os.environ.get("TENCENTCLOUD_SECRET_ID", ""),
    os.environ.get("TENCENTCLOUD_SECRET_KEY", ""),
)
if not secret_id or not secret_key:
    logger.warning("TENCENTCLOUD_SECRET_ID or TENCENTCLOUD_SECRET_KEY not set, using default credentials!")
    secret_id, secret_key = "xxx", "xxx"
cred = credential.Credential(secret_id, secret_key)
client = HunyuanClient(cred, "ap-beijing")


def query_hunyuan(messages, model="Pro", top_p=1, temperature=1, max_tokens=1024, **kwargs):
    """封装请求 hunyuan API, 参数采用 openai 格式 (client.chat.completions.create)
    API: https://cloud.tencent.com/document/api/1729/101837
        NOTE: 不支持 max_tokens 参数,
    ARGS:
        model: Pro/Std
    """
    if model.lower() == "pro":
        req = ChatCompletionsRequest()
    # elif model.lower() == "std": req = ChatStdRequest()
    else:
        raise NotImplementedError(f"model {model} not supported!")
    req._Messages = messages
    req.TopP = top_p
    req.Temperature = temperature
    # req._Model = "hunyuan-pro"
    # Hunyuan-turbo 模型默认版本，采用全新的混合专家模型（MoE）结构，相比hunyuan-pro推理效率更快，效果表现更强。
    req._Model = "hunyuan-turbo"  #! https://cloud.tencent.com/document/product/1729/104753
    req._Stream = True
    # return client.ChatPro(req)
    return client.ChatCompletions(req)


def get_nonstream_response(response) -> str:
    ret = ""
    for r in response:
        data = json.loads(r["data"])
        content = data["Choices"][0]["Delta"]["Content"]
        ret += content
    return ret


def stream_results(response) -> Iterator[str]:
    for r in response:
        data = json.loads(r["data"])
        output = data["Choices"][0]["Delta"]["Content"]
        if r:
            yield output


def hunyuan_search_full(query, stream=True, conversations=None, top_p=1, temperature=1, max_tokens=1024):
    if not conversations:
        conversations = [
            {
                "Role": "system",
                "Content": "请你扮演一个搜索引擎，帮助用户搜索并回答问题。",
            },
            {"Role": "user", "Content": query},
        ]

    response = query_hunyuan(
        model="pro",
        messages=conversations,
        top_p=top_p,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if stream:
        return stream_results(response)
    else:
        return get_nonstream_response(response)


@register_tool()
def hunyuan_search(query: str) -> Iterator[str]:
    """Use Tencent's Hunyuan API to search web

    Args:
        query (str): search query

    Returns:
        Iterator[str]: the search results
    """
    return hunyuan_search_full(query, stream=True)
