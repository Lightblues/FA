from tencentcloud.hunyuan.v20230901.models import ChatCompletionsRequest, ChatCompletionsResponse

from common import HunyuanClient
from tools.tool_hunyuan_search import hunyuan_search, query_hunyuan


client = HunyuanClient()


def test_hunyuan():
    query = "上海 天气"
    answer = hunyuan_search(query)
    for ch in answer:
        print(ch, end="", flush=True)
    print()


def test_query_hunyuan(query: str, model: str = "hunyuan-turbo"):
    conversations = [
        {"Role": "system", "Content": "请你扮演一个搜索引擎，帮助用户搜索并回答问题。"},
        {"Role": "user", "Content": query},
    ]
    res = client.query_one(model=model, messages=conversations)
    print(f"model: {model}")
    print(res)
    print()


# test_hunyuan()

for model in ["hunyuan-turbo", "hunyuan-turbo-latest", "hunyuan-pro", "hunyuan-code"]:
    test_query_hunyuan("今天上海天气如何?", model)
