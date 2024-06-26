
import os
from easonsi import utils
from easonsi.llm.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater


client = OpenAIClient()

DIR_input = "/apdcephfs/private_easonsshi/easonsshi_base/data/tongcheng/huabu_step2"
DIR_output = "/apdcephfs/private_easonsshi/easonsshi_base/data/tongcheng/huabu_step3"
os.makedirs(DIR_output, exist_ok=True)

def process_step3_get_prompt(input_json):
    return jinja_render(
        'step3_procedurecode_gen.jinja',
        input_json=input_json
    )

def process_step3(data):
    prompt = process_step3_get_prompt(data)
    response = client.query_one(prompt)
    res = Formater.remove_code_prefix(response, type="PDL")
    return res

data_names = ["114挂号", "查询运单", "标品-开发票画布", "礼金礼卡类案件"]
for data_name in data_names:
    print(f"Processing {data_name}")
    fn_input = f"{DIR_input}/{data_name}.json"
    data = utils.LoadJson(fn_input)
    res = process_step3(data)
    fn_output = f"{DIR_output}/{data_name}.txt"
    with open(fn_output, "w") as f:
        f.write(res)
    print(f"Saved to {fn_output}")