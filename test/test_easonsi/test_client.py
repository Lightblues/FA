
# %%
import os
from easonsi.llm.openai_client import OpenAIClient
client = OpenAIClient(
    base_url=os.getenv("OPENAI_PROXY_BASE_URL"),
    api_key=os.getenv("OPENAI_PROXY_API_KEY"),
)

# %%
res = client.query_one_raw("续写: 昨天", n=3)
print(res.choices)
# %%
for c in res.choices:
    print(c.message.content)
    print("-"*20)
# %%
