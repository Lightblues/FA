from fa_core.common import HunyuanClient, init_client

query = "今天上海天气如何?"


def test_openai():
    # client = init_client("gpt-4o")
    # client = init_client("test-ian")
    client = init_client("test-eason")
    res = client.query_one(query)
    print(res)

    res = client.query_one_stream(query)
    for ch in res:
        print(ch, end="", flush=True)
    print()


def test_hunyuan():
    client = HunyuanClient()
    res = client.query_one(query)
    print(res)

    res = client.query_one_stream(query)
    for ch in res:
        print(ch, end="", flush=True)
    print()


test_openai()
# test_hunyuan()
