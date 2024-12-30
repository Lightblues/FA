from fa_core.common import HunyuanClient, init_client, LLM_CFG

query = "今天上海天气如何?"


def test_config():
    print(f"> LLM_CFG: {LLM_CFG}")


def test_openai():
    # client = init_client("gpt-4o")
    # client = init_client("test-ian")
    client = init_client("test-eason")
    print(f"> client.model_name: {client.model_name}")
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


test_config()
test_openai()
# test_hunyuan()
