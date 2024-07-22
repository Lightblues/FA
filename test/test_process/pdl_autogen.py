# %%
import os, json
from tqdm import tqdm
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater
from engine_v1.common import LLM_CFG, init_client, FN_data_meta, DIR_data_base

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

def gen_by_NL_02(client: OpenAIClient, NL:str):
    # step 2: Nl -> PDL
    prompt = jinja_render("PDL_autogen_v1_meta2PDL.jinja", NL=NL)
    res = client.query_one_stream(prompt)
    r = Formater.parse_codeblock(res, type="PDL")
    return r

nl = """ {
    "PDL_name": "商品退款",
    "PDL_description": "给用户提供退款服务, 检查是否满足退款要求",
    "PDL_detailed_description": "首先, 询问用户所咨询的订单号, 通过API检查是否存在, 若不存在, 则告知用户重新输入订单号. 若存在, 则进一步询问用户退款理由. 若用户选择7天无条件退款, 则查询API是否满足购买时间为近7天的推荐要求, 若满足则调用API完成退款, 并回复用户; 否则告知用户不满足该条件, 可选择其他退款理由. 若用户选择因商品质量问题退款, 则请用户描述质量问题, 将用户提交的相关信息调用API来提交退款审核, 并回复用户已提交审核请耐心等待. 若用户选择其他原因, 则调用API转为人工服务. "
} """
res = gen_by_NL_02(client, nl)
# %%
