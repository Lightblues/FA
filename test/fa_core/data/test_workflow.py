import pytest
from fa_core.data import FAWorkflow


@pytest.mark.unit
class TestFAWorkflow:
    def test_init_with_dataset_and_id(self):
        workflow = FAWorkflow(workflow_dataset="v241127", workflow_id="000")
        data = workflow.model_dump()
        assert data["workflow_dataset"] == "v241127"
        assert data["workflow_id"] == "000"

    def test_init_from_config(self, config_default):
        workflow = FAWorkflow.from_config(config_default)
        data = workflow.model_dump()

    @pytest.mark.parametrize("invalid_id", ["", None, "999999"])
    def test_invalid_workflow_id(self, invalid_id):
        """test invalid workflow id"""
        with pytest.raises(ValueError):
            FAWorkflow(workflow_dataset="v241127", workflow_id=invalid_id)
