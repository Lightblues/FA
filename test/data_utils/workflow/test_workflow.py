from data_utils.workflow import DataManager


dm = DataManager()
workflow = dm.get_workflow_by_id("001")


def test_workflow():
    print(workflow)
    print()


def test_check_edges():
    """Check the edge infos for PDL conversion
    1. check that the source and target are valid node ids
    2. is it ture that only `source, target` are needed for PDL conversion?
    """
    for edge in workflow.Edges:
        if (edge.source not in workflow.node_id_to_node) or (edge.target not in workflow.node_id_to_node):
            raise ValueError(f"Invalid edge: {edge}")
    print("check edges passed!")


test_workflow()
# test_check_edges()
