from common import Config
from data import DataHandler


cfg = Config.from_yaml("default.yaml")
cfg.workflow_dataset = "PDL"
cfg.user_profile_id = 0

data_handler = DataHandler.create(cfg)
_dict = data_handler.model_dump()
print(_dict)


def test_workflow_str():
    print(data_handler.to_str())
    print(data_handler.pdl.to_str_wo_api())
    # print(workflow.pdl)
