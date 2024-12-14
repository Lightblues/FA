from data_utils.workflow import DataManager, WorkflowNodeBase, WorkflowEdge, Workflow

dm = DataManager()
def test_workflow():
    workflow_dict = dm.get_workflow_by_id("001")
    workflow = Workflow(**workflow_dict)
    print(workflow.Nodes[1])
    print()
