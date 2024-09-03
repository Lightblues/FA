""" 
- 基于 API code 生成标准化的API信息

input: api_definitions/*.py
output: api_schemas/*.json
    ./api_infos.json
"""

# %%
import json, os
from utils.jinja_templates import jinja_render
from engine import init_client, LLM_CFG
from easonsi.llm.openai_client import OpenAIClient, Formater

client = init_client(llm_cfg=LLM_CFG["gpt-4o"])

modules = os.listdir("./api_definitions")
modules = [m for m in modules if m.endswith(".py") and m.startswith("m0")]
for m in modules:
    flow_name = os.path.splitext(m)[0][1:].replace("_", "-")
    ofn = f"api_schemas/{flow_name}.json"
    if os.path.exists(ofn):
        print(f"[INFO] {flow_name} exists! return!")
        continue
    API_str = open(f"./api_definitions/{m}").read()
    prompt = jinja_render("data_utils/api_schema_to_standard_json.jinja", API=API_str)
    llm_response = client.query_one_stream(prompt)
    json_response = Formater.parse_llm_output_json(llm_response)
    # postprocess
    for api in json_response:
        api["from"] = flow_name
    with open(ofn, "w") as f:
        json.dump(json_response, f, indent=2, ensure_ascii=False)

# %%
import re, json
def replace_domain(url:str, new_domain:str) -> str:
    pattern = r"(http://|https://)([^/]+)"
    match = re.match(pattern, url)
    if match:
        # protocol = match.group(1)
        domain = match.group(2)
        return url.replace(domain, new_domain)
    else:
        print(f"Invalid URL: {url}")
        return url

api_infos = []
for fn in sorted(os.listdir("api_schemas")):
    with open(f"api_schemas/{fn}", "r") as f:
        apis = json.load(f)
    for api in apis:
        api["URL"] = replace_domain(api["URL"], "www.easonsi.site:9390")
        api_infos.append(api)
    print(f"  # apis of {fn}: {len(apis)}")
ofn = "api_infos.json"
with open(ofn, "w") as f:
    json.dump(api_infos, f, indent=2, ensure_ascii=False)
# %%
