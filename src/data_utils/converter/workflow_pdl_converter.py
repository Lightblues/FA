""" 
@241214
- [ ] buld typing for workflow
    - [x] nodes (node data)
    - [ ] input / output (reference)
@241216
- [ ] implement to_pdl() for each node
    - [ ] params
    - [x] ANSWER
    - [x] TOOL
    - [ ] LOGIC_EVALUATOR

TODO:
- [ ] use LLM to generate summary for each node
- [ ] draw node graph (e.g. with graphviz | pyecharts)

- [ ] finish convert for `001: 同程开发票`!
    nodes: ANSWER, PARAMETER_EXTRACTOR, TOOL, LOGIC_EVALUATOR
"""

from typing import List
from ..workflow import DataManager, Workflow, Parameter
from pdl.typings import PDL

VALID_NODE_TYPES = ("START", "ANSWER", "PARAMETER_EXTRACTOR", "TOOL", "LOGIC_EVALUATOR")

class WorkflowPDLConverter:
    def __init__(self, data_version: str="huabu_1127", export_version: str="export-1732628942") -> None:
        self.data_version = data_version
        self.export_version = export_version
        self.data_manager = DataManager(data_version, export_version)

    def convert(self, workflow_id: str):
        # 1. load the workflow
        workflow = self.data_manager.get_workflow_by_id(workflow_id)
        assert all(node.NodeType in VALID_NODE_TYPES for node in workflow.Nodes), f"Invalid node type found in workflow, valid types: {VALID_NODE_TYPES}"
        # 2. convert the nodes
        APIs = []; ANSWERs = []
        for node in workflow.Nodes:
            if node.NodeType == "TOOL":
                APIs.append(node.to_pdl())
            elif node.NodeType == "ANSWER":
                ANSWERs.append(node.to_pdl())
        params = [p for p in self.data_manager.parameter_infos.values() if p.workflow_id == workflow.WorkflowID]
        SLOTs = [p.to_pdl() for p in params]
        # 3. convert the workflow procedure
        procedure = ""
        ...
        # 4. build the PDL
        pdl = PDL(
            Name=workflow.WorkflowName,
            Desc=workflow.WorkflowDesc,
            APIs=APIs,
            SLOTs=SLOTs,
            ANSWERs=ANSWERs,
            Procedure=procedure
        )
        return pdl
    

    def build_edge_graph(self, workflow: Workflow):
        """Build the edge graph from the nodes and edges.
        - [ ] use LLM to summarize each node?
        - [ ] generate node dependency graph? 
        """
        node_id_to_name = {node.NodeID: node.NodeName for node in workflow.Nodes}
        g_edges = []
        for edge in workflow.Edges:
            g_edges.append((node_id_to_name[edge.source], node_id_to_name[edge.target]))
        return g_edges
