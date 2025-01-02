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
    - [x] LOGIC_EVALUATOR
@241220
- [x] finish convert for `001: 同程开发票`!
    nodes: ANSWER, PARAMETER_EXTRACTOR, TOOL, LOGIC_EVALUATOR
@241230
- [x] #data register data infos in unified `dataset/dataset_infos.yaml`

TODO:
- [ ] #feat use LLM to generate summary for each node
- [ ] #feat support AND/OR dependency controller
- [ ] #feat generate dependency automatically
- [ ] #vis draw node graph (e.g. with graphviz | pyecharts)
- [ ] check the API/tools after conversion (post check)
"""

import json
import yaml
import tqdm
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel
from fa_core.common import Formater, init_client, BaseClient
from fa_core.data import PDL

from ..workflow import WorkflowDataManager, Parameter, Workflow
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


class WorkflowPDLConverter(BaseModel):
    data_version: str = "v241127"
    export_version: str = "export-1732628942"
    llm_name: str = "gpt-4o"
    output_version: str = "pdl_converted_20241221_4o"
    max_workers: int = 10

    data_manager: WorkflowDataManager = None
    llm: BaseClient = None

    def model_post_init(self, __context: Any) -> None:
        self.data_manager = WorkflowDataManager(data_version=self.data_version, export_version=self.export_version)
        self.llm = init_client(self.llm_name, **llm_kwargs)

    def convert_all(self):
        """Convert the whole dataset with multi-threading.

        Output structure: `DIR_dataset / self.output_version`
        """
        task_infos = self.data_manager.get_task_infos()
        workflow_ids = sorted(task_infos.keys())

        # 1. prepare the output dir
        odir = self.data_manager.DIR_dataset / self.output_version
        for _subdir in ["pdl", "tools", "debug"]:
            (odir / _subdir).mkdir(parents=True, exist_ok=True)
        print(f">>> output dir: {odir}")

        # 2. convert each workflow
        def process_workflow(workflow_id):
            res = self.convert_one(workflow_id)
            if res is None:
                return None
            with open(odir / "pdl" / f"{workflow_id}.yaml", "w") as f:
                f.write(res["pdl"].to_str(add_procedure=True))
            with open(odir / "tools" / f"{workflow_id}.yaml", "w") as f:
                tools = [tool.model_dump() for tool in res["tools"]]
                f.write(yaml.dump(tools, sort_keys=False, allow_unicode=True))
            with open(odir / "debug" / f"{workflow_id}_llm_prompt.txt", "w") as f:
                f.write(res["llm_prompt"])
            with open(odir / "debug" / f"{workflow_id}_llm_response.txt", "w") as f:
                f.write(res["llm_response"])
            return workflow_id

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            success_ids = list(tqdm.tqdm(executor.map(process_workflow, workflow_ids), total=len(workflow_ids)))
            success_ids = [id for id in success_ids if id is not None]
            print(f">>> {len(success_ids)}/{len(workflow_ids)} workflows converted successfully")

        # 3. record the conversion infos
        with open(odir / "task_infos.json", "w") as f:
            task_infos = {k: v for k, v in task_infos.items() if k in success_ids}
            out = {
                "version": self.data_version,
                "task_infos": task_infos,
            }
            f.write(json.dumps(out, ensure_ascii=False, indent=4))

        # 3.2 add the task infos to dataset_infos.yaml
        with open(self.data_manager.DIR_dataset / "dataset_infos.yaml", "r") as f:
            dataset_infos = yaml.load(f, Loader=yaml.FullLoader)
        dataset_infos[self.output_version] = {
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "extra": {
                "llm_name": self.llm_name,
                "data_version": self.data_version,
                "export_version": self.export_version,
            },
        }
        with open(self.data_manager.DIR_dataset / "dataset_infos.yaml", "w") as f:
            yaml.dump(dataset_infos, f, sort_keys=False, allow_unicode=True)

    def convert_one(self, workflow_id: str):
        # 1. load the workflow
        try:
            workflow = self.data_manager.get_workflow_by_id(workflow_id)
            assert all(node.NodeType in VALID_NODE_TYPES for node in workflow.Nodes), f"Invalid node type found in workflow {workflow_id}"
        except Exception as e:
            print(f"[WARNING] {workflow_id} {e}")
            return None
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
