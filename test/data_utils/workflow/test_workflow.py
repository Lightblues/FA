from data_utils.workflow import DataManager, WorkflowNodeBase, WorkflowEdge, Workflow

dm = DataManager()

def test_workflow():
    workflow = dm.get_workflow_by_id("001")
    print(workflow)

    assert workflow.check_edges()
    print("check edges passed!")

test_workflow()
