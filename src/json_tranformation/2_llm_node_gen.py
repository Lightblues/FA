
import os
from tqdm import tqdm
from easonsi import utils
from easonsi.llm.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater

client = OpenAIClient()

DIR_input = "../data/demo/huabu_step1"
DIR_output = "../data/demo/huabu_step2"
os.makedirs(DIR_output, exist_ok=True)
# DIR_output2 = "../data/demo/huabu_step2_2"
# os.makedirs(DIR_output2, exist_ok=True)

def process_step2_get_prompt(input_json):
    return jinja_render(
        'step2_node_desc.jinja',
        input_json=input_json
    )

def process_step2(data, n_nodes_per_prompt=50):
    nodes = data["Nodes"]
    nodes_processed = []
    for i in tqdm(range(0, len(nodes), n_nodes_per_prompt)):
        input_json = {
            'TaskFlowName': data['TaskFlowName'],
            'TaskFlowDesc': data['TaskFlowDesc'],
            "Nodes": nodes[i:i+n_nodes_per_prompt]
        }
        prompt = process_step2_get_prompt(input_json)
        response = client.query_one(prompt)
        errcode, res = Formater.parse_llm_output_json(response)
        if errcode != 0:
            print(f"[error] errcode={errcode}")
            break
        nodes_processed.extend(res['Nodes'])
    return nodes_processed

def replace_nodes(nodes, nodes_processed):
    node_id_to_idx = {}
    for idx, node in enumerate(nodes):
        node_id_to_idx[node["NodeID"]] = idx
    ids_all = set([node["NodeID"] for node in nodes])
    ids_matched = set()
    for node in nodes_processed:
        idx = node_id_to_idx.get(node["NodeID"], None)
        if idx is not None:
            node["Branches"] = nodes[idx].get("Branches", {})
            nodes[idx] = node
            ids_matched.add(node["NodeID"])
    ids_missed = ids_all - ids_matched
    print(f"[warning] missed nodes: {ids_missed}")
    return nodes

def process_step2_branch_get_prompt(input_json):
    return jinja_render(
        'step2_node_branch.jinja',
        input_json=input_json
    )

def process_step2_branch(data, n_nodes_per_prompt=50):
    # TODO: implement this!
    nodes = data["Nodes"]
    nodes_processed = []
    for i in tqdm(range(0, len(nodes), n_nodes_per_prompt)):
        input_json = {
            'TaskFlowName': data['TaskFlowName'],
            'TaskFlowDesc': data['TaskFlowDesc'],
            "Nodes": nodes[i:i+n_nodes_per_prompt]
        }
        prompt = process_step2_get_prompt(input_json)
        response = client.query_one(prompt)
        errcode, res = Formater.parse_llm_output_json(response)
        if errcode != 0:
            print(f"[error] errcode={errcode}")
            break
        nodes_processed.extend(res['Nodes'])
    return nodes_processed

# _data_name = "标品-开发票画布"
data_names = ["114挂号", "查询运单", "标品-开发票画布", "礼金礼卡类案件"]
for _data_name in data_names:
    _ofn = f"{DIR_output}/{_data_name}.json"
    # if os.path.exists(_ofn):
    #     print(f"[warning] {_ofn} exists, skip")
    #     continue
    fn_input = f"{DIR_input}/{_data_name}.json"
    data = utils.LoadJson(fn_input)
    print(f"[info] processing {_data_name}")
    nodes_processed = process_step2(data)
    data["Nodes"] = replace_nodes(data["Nodes"], nodes_processed)
    utils.SaveJson(data, _ofn)
    print(f"[info] saved to {_ofn}")