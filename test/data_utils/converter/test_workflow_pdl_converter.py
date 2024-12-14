from data_utils.converter.workflow_pdl_converter import WorkflowPDLConverter

converter = WorkflowPDLConverter()
workflow = converter.data_manager.get_workflow_by_id("001")
g = converter.build_edge_graph(workflow)
print(g)
print()