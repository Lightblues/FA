"""
@241214
- [x] buld typing for workflow
    - [x] nodes (node data)
    - [x] input / output (reference)
    --> rewriten with @proto3
@241216
- [x] implement to_pdl() for each node
    - [x] params
    - [x] ANSWER
    - [x] TOOL
    - [ ] LOGIC_EVALUATOR
@241220
- [x] finish convert for `001: 同程开发票`!
    nodes: ANSWER, PARAMETER_EXTRACTOR, TOOL, LOGIC_EVALUATOR

TODO:
- [ ] use LLM to generate summary for each node
- [ ] draw node graph (e.g. with graphviz | pyecharts)
"""

import json
from typing import Dict, List

from fa_core.common import LLM_CFG, Formater, init_client
from data.pdl import PDL

from ..workflow import DataManager, Parameter, Workflow
from ..workflow.base import NodeType
from . import prompts


VALID_NODE_TYPES = (
    NodeType.START,
    NodeType.ANSWER,
    NodeType.PARAMETER_EXTRACTOR,
    NodeType.TOOL,
    NodeType.LOGIC_EVALUATOR,
    NodeType.LLM,
    NodeType.CODE_EXECUTOR,
)

llm_kwargs = {
    "temperature": 0.0,
    "max_completion_tokens": 8192,  # for long PDL!
}


class WorkflowPDLConverter:
    def __init__(
        self,
        data_version: str = "v241127",
        export_version: str = "export-1732628942",
        llm_name: str = "gpt-4o",
    ) -> None:
        self.data_manager = DataManager(data_version=data_version, export_version=export_version)
        self.llm = init_client(llm_name, **llm_kwargs)

    def convert(self, workflow_id: str):
        # 1. load the workflow
        workflow = self.data_manager.get_workflow_by_id(workflow_id)
        assert all(
            node.NodeType in VALID_NODE_TYPES for node in workflow.Nodes
        ), f"Invalid node type found in workflow, valid types: {VALID_NODE_TYPES}"
        # 2. convert the nodes
        tools = []
        APIs = []
        ANSWERs = []
        for node in workflow.Nodes:
            if node.NodeType in (NodeType.TOOL, NodeType.CODE_EXECUTOR, NodeType.LLM):
                APIs.append(node.to_pdl())
                tools.append(node.to_tool_spec())
            elif node.NodeType == NodeType.ANSWER:
                ANSWERs.append(node.to_pdl())
        params = [p for p in self.data_manager.parameter_infos.values() if p.workflow_id == workflow.WorkflowID]
        SLOTs = [p.to_pdl() for p in params]
        # 3. convert the workflow procedure
        res = self._convert_procedure(workflow, params)
        # 4. build the PDL
        pdl = PDL(
            Name=workflow.WorkflowName,
            Desc=workflow.WorkflowDesc,
            APIs=APIs,
            SLOTs=SLOTs,
            ANSWERs=ANSWERs,
            Procedure=res["procedure"],
        )
        return {
            "pdl": pdl,
            "tools": tools,
            "llm_prompt": res["llm_prompt"],
            "llm_response": res["llm_response"],
        }

    def _convert_procedure(self, workflow: Workflow, params: List[Parameter]) -> Dict[str, str]:
        """Convert the workflow procedure to a string"""
        meta = f"Name: {workflow.WorkflowName}\nDesc: {workflow.WorkflowDesc}"
        nodes = "\n".join([str(node) for node in workflow.Nodes])
        edges = "\n".join([f"{edge.source} -> {edge.target}" for edge in workflow.Edges])
        params = "\n".join([str(p) for p in params])
        llm_prompt = prompts.template_procudure.format(meta=meta, nodes=nodes, edges=edges, params=params)
        print(f"> querying llm for workflow {workflow.WorkflowID}...")
        llm_response = self.llm.query_one(llm_prompt)
        print(f">   done, llm_response: {json.dumps(llm_response[:50], ensure_ascii=False)}...")
        procedure = Formater.parse_codeblock(llm_response, "python")
        return {
            "llm_prompt": llm_prompt,
            "llm_response": llm_response,
            "procedure": procedure,
        }

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
