from data_utils.workflow import WorkflowDataManager


dm = WorkflowDataManager()


def test_LLM_to_tool():
    #
    workflow_id = "006"  # GuaHao, with LLM nodes
    workflow = dm.get_workflow_by_id(workflow_id)
    node = workflow.Nodes[38]
    print(node)
    print(node.to_tool_spec())
    print()


def test_code_executor_to_tool():
    # code: use Inputs/Outputs as function parameters
    workflow_id = "006"  # GuaHao, with LLM nodes
    workflow = dm.get_workflow_by_id(workflow_id)
    node = workflow.Nodes[19]
    print(node)
    print(node.to_tool_spec())
    print()


def test_check_edges():
    """Check the edge infos for PDL conversion
    1. check that the source and target are valid node ids
    2. is it ture that only `source, target` are needed for PDL conversion?
    """
    workflow_id = "006"  # GuaHao, with LLM nodes
    workflow = dm.get_workflow_by_id(workflow_id)

    for edge in workflow.Edges:
        if (edge.source not in workflow.node_id_to_node) or (edge.target not in workflow.node_id_to_node):
            raise ValueError(f"Invalid edge: {edge}")
    print("check edges passed!")


test_LLM_to_tool()
test_code_executor_to_tool()
# test_check_edges()
