from data_utils.converter.workflow_pdl_converter import WorkflowPDLConverter

converter = WorkflowPDLConverter()
workflow = converter.data_manager.get_workflow_by_id("001")

def test_build_edge_graph():
    g = converter.build_edge_graph(workflow)
    print(g)

def test_nodes_to_pdl():
    for node in workflow.Nodes:
        converted_node = node.to_pdl()
        print(f"--- {node.NodeName} ---\n{node}\n---\n{converted_node}\n\n")

# test_build_edge_graph()
# test_nodes_to_pdl()

def test_convert():
    pdl = converter.convert("001")
    print(pdl)

test_convert()
