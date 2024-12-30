from fa_core.common import HunyuanClient, init_client, LLM_CFG

query = "今天上海天气如何?"


def test_config():
    print(f"> LLM_CFG: {LLM_CFG}")


def test_model_name():
    client = init_client("gpt-4o")
    # client = init_client("test-ian")
    # client = init_client("test-eason")
    print(f"> client.model_name: {client.model_name}")
    res = client.query_one(query)
    print(res)

    res = client.query_one_stream(query)
    for ch in res:
        print(ch, end="", flush=True)
    print()


def test_seed():
    # kwargs = {}
    # kwargs = {"seed": 42, "temperature": 0.0}
    kwargs = {"seed": 42, "temperature": 1.0}
    # client = init_client("gpt-4o", **kwargs)      # NOTE: 对于 4o, 可能返回的结果可能和机器 ID 相关 (reponse中包含该信息)
    client = init_client("test-eason", **kwargs)  # 同一机器上的 vllm 可以保证结果一致!
    for i in range(5):
        res = client.query_one(query)
        print(res)


def test_hunyuan():
    client = HunyuanClient()
    res = client.query_one(query)
    print(res)

    res = client.query_one_stream(query)
    for ch in res:
        print(ch, end="", flush=True)
    print()


# test_config()
# test_model_name()
test_seed()
# test_hunyuan()
