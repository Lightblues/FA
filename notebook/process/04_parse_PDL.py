"""
解析PDL语法, 见 [datamodel]
"""

# %%
DIR_data = "../../data/v240628/huabu_step3/"
fn = f"{DIR_data}/000-114挂号.txt"
with open(fn, "r", encoding="utf-8") as f:
    text = f.read()
apis, requests, answers, meta, workflow = text.split("\n\n")


# %%
def parse_apis(s: str):
    apis = s.split("\n-")[1:]
    res = []
    for s_api in apis:
        api = {}
        for line in s_api.strip().split("\n"):
            k, v = line.strip().split(":", 1)
            api[k.strip()] = v.strip()
        res.append(api)
    return res


apis = parse_apis(apis)
# %%
requests = parse_apis(requests)
# %%
answers = parse_apis(answers)
answers
# %%
import re


def parse_meta(s: str):
    """recognize `TaskFlowName: {}` and `TaskFlowDesc: {}`"""
    reg_taskflow = re.compile(r"TaskFlowName: (.+)")
    reg_taskflow_desc = re.compile(r"TaskFlowDesc: (.+)")
    taskflow = reg_taskflow.search(s).group(1)
    taskflow_desc = reg_taskflow_desc.search(s).group(1)
    return taskflow, taskflow_desc


parse_meta(meta)
# %%
