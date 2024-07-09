""" 
利用LLM自动化地构造数据. see [process/data_gen/PDL_to_conversation.py]
@easonsshi 240709
"""

# %%
import os
_file_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(f"{_file_dir}/../../src")
from engine_v1.datamodel import PDL
from engine_v1.common import DIR_data

from engine_v1.common import DIR_data, init_client, LLM_CFG, DIR_apis
client = init_client(llm_cfg=LLM_CFG["gpt-4o"])


pdl = PDL()
workflow_name = "004-服务网点查询"
workflow_name = "022-挂号"
pdl.load_from_file(f"{DIR_data}/{workflow_name}.txt")

from utils.jinja_templates import jinja_render
prompt = jinja_render("PDL_to_conversation_gen.jinja", PDL=pdl.PDL_str)
print(prompt)

# %%
# NOTE: 直接用这个参数n来控制多个生成, 好像效果不好!!!
# res = client.query_one_raw(prompt, n=5, temperature=.7)
# for c in res.choices:
#     print(c.message.content)
#     print("-"*20)

res = client.query_one_stream(prompt)

# %%
import re
from easonsi.llm.openai_client import Formater
# def parse_res(s:str):
#     s = Formater.parse_codeblock(s, type="conversation")
#     # split s by `--- Conversation * ---`
#     re_pattern = r"--- Conversation \d+ ---"
#     res = re.split(re_pattern, s)
#     ans = []
#     for r in res:
#         r = r.strip()
#         if r: ans.append(r)
#     return ans
# ans = parse_res(res)

# %%
import json
r = Formater.parse_codeblock(res, type="json")
r = json.loads(r)
print(len(r))
# %%
