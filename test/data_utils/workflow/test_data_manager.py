"""
EDA: explore dumped workflow data

@241213
- [x] 1. check all node types; 2. check each node type; 3. stat node type
"""

from typing import *

from data_utils.workflow import NODE_TYPE_KEY_MAP, WORKFLOW_NODE_TYPES, DataManager


data_manager = DataManager()


def get_all_nodes_by_type(node_type: str, workflow_id: Union[str, int] = None):
    """Get all nodes of a specific type
    NOTE: only used when EDA
    """
    workflow_ids = list(data_manager.workflow_infos.keys()) if workflow_id is None else [data_manager.get_standard_workflow_id(workflow_id)]
    nodes_all = []
    for workflow_id in workflow_ids:
        workflow = data_manager.get_workflow_by_id(workflow_id, return_dict=True)
        for node in workflow["Nodes"]:
            if node["NodeType"] == node_type:
                nodes_all.append(node)
    return nodes_all


# 1. check all node types
def check_all_node_types():
    """check the possible node types
    > NoteType: {'CODE_EXECUTOR', 'PARAMETER_EXTRACTOR', 'LLM', 'LLM_KNOWLEDGE_QA', 'LOGIC_EVALUATOR', 'ANSWER', 'KNOWLEDGE_RETRIEVER', 'START', 'TOOL'}
    """
    node_types = set()
    for workflow_id, workflow_info in data_manager.workflow_infos.items():
        workflow = data_manager.get_workflow_by_id(workflow_id)
        for node in workflow.Nodes:
            node_types.add(node.NodeType)
    print(f"> all node types: {node_types}")
    return node_types


# 2. check each node type
def check_node_type():
    def print_node_properties(node: Dict):
        # CODE_EXECUTOR -> CodeExecutorNodeData
        # node_type_camel = node['NodeType'].title().replace("_", "") + "NodeData"  # NOTE: error, because LLM -> LLMNodeData
        node_data = node[NODE_TYPE_KEY_MAP[node["NodeType"]]]
        s = f"--- {node['NodeType']} ---\n [{node['NodeName']}] {node['NodeID']}\n  desc: {node['NodeDesc']}\n  node_data: {node_data}"
        print(s)
        return list(node_data.keys())

    for node_type in WORKFLOW_NODE_TYPES:
        nodes = data_manager.get_all_nodes_by_type(node_type)
        properties = print_node_properties(nodes[0])
        print(f"> {node_type}: {properties}")


# check_all_node_types()
# check_node_type()
data_manager.stat_node_type()
