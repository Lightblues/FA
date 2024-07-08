#%%
from easonsi.llm.openai_client import Formater

s = """ 
some thing
```json
{
    "a": 1
}
```
bala bala
```py
import os
```
"""
res_json = Formater.parse_codeblock(s, type="json")
print(res_json)
res_py = Formater.parse_codeblock(s, type="py")
print(res_py)

# %%
