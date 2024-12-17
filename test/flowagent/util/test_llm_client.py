from common import LLM_CFG, init_client


client = init_client(LLM_CFG["gpt-4o"])

res = client.query_one("Hello, how are you?")
print(res)
