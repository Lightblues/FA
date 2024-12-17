from common import LLM_CFG, init_client


client = init_client(llm_cfg=LLM_CFG["debug"])


def test_query_one():
    print(f"> sending: hello")
    res = client.query_one("hello")
    print(res)


def test_query_one_stream():
    print(f"> sending: hello")
    res = client.query_one_stream("hello")
    for c in res:
        print(c, end="")


test_query_one_stream()
print()
