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
from tencentcloud.hunyuan.v20230901.models import ChatCompletionsRequest, ChatCompletionsResponse

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


def query_hunyuan(messages, model="hunyuan-turbo", top_p=1, temperature=1, stream=False, enable_enhancement=False):
    """封装请求 hunyuan API, 参数采用 openai 格式 (client.chat.completions.create)
    API: https://cloud.tencent.com/document/api/1729/101837
        NOTE: 不支持 max_tokens 参数,
    """
    req = ChatCompletionsRequest()
    req._Messages = messages
    req.TopP = top_p
    req.Temperature = temperature
    req._Model = model  #! https://cloud.tencent.com/document/product/1729/104753
    req._Stream = stream
    req._EnableEnhancement = enable_enhancement
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


def hunyuan_search_full(query, stream=True, conversations=None, top_p=1, temperature=1, enable_enhancement=False):
    if not conversations:
        conversations = [
            {"Role": "system", "Content": "请你扮演一个搜索引擎，帮助用户搜索并回答问题。"},
            {"Role": "user", "Content": query},
        ]

    response = query_hunyuan(
        model="hunyuan-turbo",  # NOTE: use the best one
        messages=conversations,
        top_p=top_p,
        temperature=temperature,
        enable_enhancement=enable_enhancement,
        stream=stream,
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
