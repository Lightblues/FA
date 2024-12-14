from data_utils.workflow import DataManager, WorkflowNodeBase, WorkflowEdge, Workflow

dm = DataManager()

def test_workflow():
    workflow = dm.get_workflow_by_id("001")
    print(workflow.Nodes[1])
    print()

test_workflow()
