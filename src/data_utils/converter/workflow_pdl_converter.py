""" 
TODO:
- [ ] buld typing for workflow
    - [ ] nodes (node data)
    - [ ] input / output (reference)
- [ ] use LLM to generate summary for each node
- [ ] draw node graph (e.g. with graphviz | pyecharts)
- [ ] implement WorkflowPDLConverter
"""

from ..workflow import DataManager, Workflow

class WorkflowPDLConverter:
    def __init__(self, data_version: str="huabu_1127", export_version: str="export-1732628942") -> None:
        self.data_version = data_version
        self.export_version = export_version
        self.data_manager = DataManager(data_version, export_version)

    def convert(self, workflow_id: str):
        workflow = self.data_manager.get_workflow_by_id(workflow_id)
        g = self.build_edge_graph(workflow)
        print(g)
    
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
