from flowagent.utils import init_client, LLM_CFG

client = init_client(LLM_CFG["gpt-4o"])

res = client.query_one("Hello, how are you?")
print(res)
