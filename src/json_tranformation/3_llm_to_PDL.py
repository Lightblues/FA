
import os, sys
from tqdm import tqdm
import concurrent.futures
from easonsi import utils
from easonsi.llm.openai_client import OpenAIClient, Formater
sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))] + sys.path
from utils.jinja_templates import jinja_render

client = OpenAIClient(
    model_name="gpt-4o",
    base_url=os.getenv("OPENAI_PROXY_BASE_URL"),
    api_key=os.getenv("OPENAI_PROXY_API_KEY")
)

DIR_input = "../../data/v240628/huabu_step2"
DIR_output = "../../data/v240628/huabu_step3"
os.makedirs(DIR_output, exist_ok=True)

def process_step3_get_prompt(input_json):
    return jinja_render(
        'step3_procedurecode_gen.jinja',
        input_json=input_json
    )

def process_step3(data, ofn: str):
    print(f"[info] Processing {data['TaskFlowName']}")
    prompt = process_step3_get_prompt(data)
    response = client.query_one(prompt)
    res = Formater.remove_code_prefix(response, type="PDL")
    with open(ofn, "w") as f:
        f.write(res)
    print(f"[info] Saved to {ofn}")
    return res

# data_names = ["114挂号", "查询运单", "标品-开发票画布", "礼金礼卡类案件"]
# for data_name in data_names:
#     print(f"Processing {data_name}")
#     fn_input = f"{DIR_input}/{data_name}.json"
#     data = utils.LoadJson(fn_input)
#     res = process_step3(data)
#     fn_output = f"{DIR_output}/{data_name}.txt"
#     with open(fn_output, "w") as f:
#         f.write(res)
#     print(f"Saved to {fn_output}")
data_names = os.listdir(DIR_input)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for fn in data_names:
        _ofn = f"{DIR_output}/{fn}".replace("json", "txt")
        if os.path.exists(_ofn):
            with open(_ofn, 'r') as f: content = f.read().strip()
            if content:
                print(f"[warning] {_ofn} exists, skip")
                continue
        data = utils.LoadJson(f"{DIR_input}/{fn}")
        future = executor.submit(process_step3, data, _ofn)
        futures.append(future)
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        try:
            res_ = future.result()
        except Exception as e:
            print(f"[ERROR] for future: {future}\n{e}")
            for f in futures:
                f.cancel()
            raise e