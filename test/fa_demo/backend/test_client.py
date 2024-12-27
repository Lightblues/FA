from fa_demo.backend import FrontendClient
from fa_core.common import Config
from fa_demo.backend.typings import InspectGetWorkflowQuery, SingleRegisterRequest

client = FrontendClient(backend_url="http://localhost:8101")


def test_client():
    response = client.inspect_get_workflow("123", InspectGetWorkflowQuery(config=Config.from_yaml("default.yaml")))
    workflow = response.workflow
    print(workflow)


test_client()
