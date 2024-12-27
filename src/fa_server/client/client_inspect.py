from typing import Dict
import requests

from ..typings import InspectGetWorkflowQuery, InspectGetWorkflowResponse
from .client_base import BaseClient


class InspectClient(BaseClient):
    def inspect_get_workflow(self, conversation_id: str, workflow_dataset: str, workflow_id: str) -> InspectGetWorkflowResponse:
        url = f"{self.backend_url}/inspect_get_workflow/{conversation_id}"
        request = InspectGetWorkflowQuery(workflow_dataset=workflow_dataset, workflow_id=workflow_id)
        response = requests.get(url, json=request.model_dump())
        if response.status_code == 200:
            return InspectGetWorkflowResponse(**response.json())
        else:
            raise Exception(f"Error: {response.text}")
