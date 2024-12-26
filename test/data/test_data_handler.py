from fa_core.common import Config
from fa_core.data import FAWorkflow


def test_data_handler():
    data_handler = FAWorkflow(workflow_dataset="PDL", workflow_id="000")
    _dict = data_handler.model_dump()
    print(_dict)


def test_data_handler_from_config():
    cfg = Config.from_yaml("default.yaml")
    cfg.workflow_dataset = "PDL"
    test_data_handler = FAWorkflow.from_config(cfg)
    _dict = test_data_handler.model_dump()
    print(_dict)


if __name__ == "__main__":
    test_data_handler()
    test_data_handler_from_config()
