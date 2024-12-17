"""给定需求之下生成规范PDL
@240714 gen_by_PDL_sample
    input: geiven sample PDL
    output: new PDLs
@240715 gen_by_NL_02: 根据NL再生成PDL
    input: given NL
    output: PDL

"""

# %%
import json
import os

from easonsi.llm.openai_client import Formater, OpenAIClient
from engine_v1.common import LLM_CFG, DIR_data_base, FN_data_meta, init_client
from tqdm import tqdm

from utils.jinja_templates import jinja_render


client = init_client(llm_cfg=LLM_CFG["gpt-4o"])


# demand = """ 查天气, 需要获取用户所需要的城市、日期等信息 """
# demand = """ 课程调整, 可以帮助用户修改上课的时间或者取消已经安排过的课程 """
def gen_by_PDL_sample(client: OpenAIClient, demand: str):
    """v00: 给定需求之下生成规范PDL, 1-shot
    但感觉效果不是很好
    """
    prompt = jinja_render("PDL_autogen_v0.jinja", demand=demand)

    res = client.query_one_stream(prompt)


def gen_by_NL_01(client: OpenAIClient):
    """v01: 基于NL的需求描述进行生成
    step 1: 基于NL拓展更多样本, few-shot
    step 2: 然后根据NL进行拓展 -> PDL
    """
    with open(FN_data_meta, "r") as f:
        data_meta = json.load(f)
    for d in data_meta:
        d.pop("id")
    selected = [0, 2]
    PDLs = [data_meta[i] for i in selected]
    prompt = jinja_render("PDL_autogen_v1_meta.jinja", PDLs=PDLs)
    res = client.query_one_stream(prompt)


def gen_by_NL_02(client: OpenAIClient, NL: str, ofn: str = None):
    # step 2: Nl -> PDL
    prompt = jinja_render("PDL_autogen_v1_meta2PDL.jinja", NL=NL)
    res = client.query_one_stream(prompt)
    r = Formater.parse_codeblock(res, type="PDL")
    if ofn is not None:
        with open(ofn, "w") as f:
            f.write(r)
    return r


if __name__ == "__main__":
    data_meta = json.load(open(FN_data_meta, "r"))
    for m in tqdm(data_meta):
        _id = m.pop("id")
        ofn = f"{DIR_data_base}/huabu_refine01/{_id}.txt"
        if os.path.exists(ofn):
            print(f"[INFO] {_id} exists! return!")
            continue
        gen_by_NL_02(client, NL=m, ofn=ofn)
