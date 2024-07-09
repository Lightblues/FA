
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

DIR_input = "../../data/v240628/huabu_step1"
DIR_output = "../../data/v240628/huabu_step2"
os.makedirs(DIR_output, exist_ok=True)
# DIR_output2 = "../data/v240628/huabu_step2_2"
# os.makedirs(DIR_output2, exist_ok=True)

def process_step2_get_prompt(input_json):
    return jinja_render(
        'step2_node_desc.jinja',
        input_json=input_json
    )


def process_nodes(data, n_nodes_per_prompt=10):
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

def process_step2(data, ofn: str, n_nodes_per_prompt=50):
    print(f"[info] processing {data['TaskFlowName']}")
    nodes_processed = process_nodes(data, n_nodes_per_prompt=n_nodes_per_prompt)
    data["Nodes"] = replace_nodes(data["Nodes"], nodes_processed)
    utils.SaveJson(data, ofn)
    print(f"[info] saved to {ofn}")


data_names = os.listdir(DIR_input)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for fn in data_names:
        _ofn = f"{DIR_output}/{fn}"
        if os.path.exists(_ofn):
            print(f"[warning] {_ofn} exists, skip")
            continue
        data = utils.LoadJson(f"{DIR_input}/{fn}")
        future = executor.submit(process_step2, data, _ofn)
        futures.append(future)
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        try:
            res_ = future.result()
        except Exception as e:
            print(f"[ERROR] for future: {future}\n{e}")
            for f in futures:
                f.cancel()
            raise e