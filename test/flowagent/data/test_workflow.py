from common import Config
from flowagent.data import DataManager, Workflow


cfg = Config.from_yaml("default.yaml")
cfg.workflow_dataset = "PDL"
cfg.user_profile_id = 0

workflow = Workflow(cfg)


def test_workflow_str():
    print(workflow.to_str())
    print(workflow.pdl.to_str_wo_api())
    # print(workflow.pdl)
