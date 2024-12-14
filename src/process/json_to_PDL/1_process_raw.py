""" 
doc: [画布转换&执行方案](https://doc.weixin.qq.com/slide/p3_AcMATAZtAPIVToQc9ODQIeVMJUBMV?scode=AJEAIQdfAAoaJOY0L7AcMATAZtAPI)

1. raw JSON, with "Edges" -> concise JSON
2. LLM convert -> standard Node descripion
3. LLM convert -> standard procedure description
"""
import os, pathlib
from tqdm import tqdm
from easonsi import utils
_DROOT = pathlib.Path(__file__).parent.parent.parent.parent / "data"
DIR_input = _DROOT / "huabu_1127/export-1732628942"
DIR_output = _DROOT / "huabu_1127/step_1"
os.makedirs(DIR_output, exist_ok=True)

def preprocess_slotmap(data):
    """ add SlotName to Request and Branches """
    slot_map = data["Snapshot"]["SlotMap"]
    nodes = data["Nodes"]
    for n in nodes:
        if "ApiNodeData" in n:
            api_data = n["ApiNodeData"]
            if "Request" in api_data:
                for r in api_data["Request"]:
                    if "SlotValueData" in r and "SlotID" in r["SlotValueData"]:
                        slot_id = r["SlotValueData"]["SlotID"]
                        if slot_id in slot_map:
                            r["SlotValueData"]["SlotName"] = slot_map[slot_id]
                            print(f"[Request] SlotID={slot_id} -> SlotName={slot_map[slot_id]}")
                        else: print(f"[warning] SlotID={slot_id} not found")
        if "Branches" in n:
            for b in n["Branches"]:
                if "ConditionInfo" in b and "Condition" in b["ConditionInfo"] and "SlotValueData" in b["ConditionInfo"]["Condition"]:
                    slot_id = b["ConditionInfo"]["Condition"]["SlotValueData"]["SlotID"]
                    if slot_id in slot_map:
                        b["ConditionInfo"]["Condition"]["SlotValueData"]["SlotName"] = slot_map[slot_id]
                        print(f"[Branch] SlotID={slot_id} -> SlotName={slot_map[slot_id]}")
                    else: print(f"[warning] SlotID={slot_id} not found")
    return data

def preprocess_paramid(data):
    """ add ParamName in Response to Branches """
    param_map = {}
    nodes = data["Nodes"]
    for n in nodes:
        if n["NodeType"] == "API":
            response = n["ApiNodeData"]["Response"]
            for r in response:
                param_map[r["ParamID"]] = r["ParamName"]
    for n in nodes:
        if "Branches" in n:
            for b in n["Branches"]:
                if "ConditionInfo" in b and "Condition" in b["ConditionInfo"]:
                    condition = b["ConditionInfo"]["Condition"]
                    if "APIRespValueData" in condition:
                        param_id = condition["APIRespValueData"]["ParamID"]
                        if param_id in param_map:
                            condition["APIRespValueData"]["ParamName"] = param_map[param_id]
                            print(f"[Branch] ParamID={param_id} -> ParamName={param_map[param_id]}")
                        else: print(f"[warning] ParamID={param_id} not found")
    return data


def build_edge_info(data):
    """ reindex edge_id, and build edge_info. DEPRECATED """
    edge_remap = {}; _id = 0
    edge_info = {}
    for e in data["Edges"]:
        edge_id = e["EdgeID"]
        if edge_id in edge_remap:
            print(f"[warning] edge_id={edge_id} already exists")
            continue
        edge_id_new = f"edge-{_id:03d}"
        edge_remap[edge_id] = edge_id_new
        _id += 1
        edge_info[edge_id_new] = e
    return edge_info, edge_remap

def build_node_info(data):
    """ reindex node_id, and build node_info"""
    node_remap = {}; _id = 0
    node_info = {}
    for n in data["Nodes"]:
        node_id = n["NodeID"]
        if node_id in node_remap:
            print(f"[warning] node_id={n['NodeID']} already exists")
            continue
        if len(node_id) > 10:
            node_id_new = f"node-{_id:03d}"
            node_remap[node_id] = node_id_new
            _id += 1
        else:
            node_remap[node_id] = node_id
        node_info[node_id] = n
    return node_info, node_remap

def process_node(node_info:dict, node_remap:dict):
    """ 
{
    'NodeID': '53c1e31b-1de5-db3a-e1c4-48257f386f4e',
    'NodeName': '会员身份查询',
    'NodeType': 'API',
    'ApiNodeData': {'API': xxx, 'Request': xxx, 'Response': xxx}
    'Branches': [
        {'ConditionInfo': xxx, 'NextNodeID': xxx},
        {'ConditionInfo': xxx, 'NextNodeID': xxx},
    ]
}
    """
    ans = []
    for nid, n in node_info.items():
        processed = {}
        processed["NodeID"] = node_remap[nid]
        processed["NodeName"] = n["NodeName"]
        processed["NodeType"] = n["NodeType"]
        # process the node-type specific data
        if n["NodeType"] == "API":
            processed["ApiNodeData"] = n["ApiNodeData"]
        elif n["NodeType"] == "ANSWER":
            processed["AnswerNodeData"] = n["AnswerNodeData"]
        elif n["NodeType"] == "REQUEST":
            processed["RequestNodeData"] = n["RequestNodeData"]
        elif n["NodeType"] in ["START"]:
            pass
        else:
            print(f"[warning] NodeType={n['NodeType']} not supported")
            print(f">> keys: {n.keys()}")
            print(f">> data: {n}")
        branches = []
        for b in n["Branches"]:
            branch = {}
            branch["ConditionInfo"] = b["ConditionInfo"]
            branch["NextNodeID"] = node_remap[b["NextNodeID"]]
            branches.append(branch)
        processed["Branches"] = branches
        ans.append(processed)
    return ans

def get_final(data, processed_nodes):
    """ 
{
    "TaskFlowName": "同程开发票",
    "TaskFlowDesc": "咨询开具发票的方法",
    "Nodes": [node1, node2, ...],
    "Edges": [{"Label": "开票方式 = 平台开具", xxx} // TODO: add the edge info to branch
    "Snapshot": {
        "SlotMap": { "88e4ae53-ca9b-4b60-b089-f0efe521e0e3": "订单编号", ... },
    }
}
    """
    ans = {}
    ans["TaskFlowName"] = data["TaskFlowName"]
    ans["TaskFlowDesc"] = data["TaskFlowDesc"]
    ans["Nodes"] = processed_nodes
    return ans


# data_names = ["114挂号", "查询运单", "标品-开发票画布", "礼金礼卡类案件"]
data_names = os.listdir(DIR_input)
data_names = [fn for fn in data_names if fn.endswith(".json")]
for fn in tqdm(data_names):
    data = utils.LoadJson(f"{DIR_input}/{fn}")
    print(f"Processing {fn}")

    data = preprocess_slotmap(data)
    data = preprocess_paramid(data)

    node_info, node_remap = build_node_info(data)
    processed_nodes = process_node(node_info, node_remap)
    final = get_final(data, processed_nodes)
    _ofn = f"{DIR_output}/{fn}"
    utils.SaveJson(final, _ofn)
    print(f"Saved to {_ofn}")
