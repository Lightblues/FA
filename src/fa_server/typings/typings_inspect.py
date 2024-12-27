from fa_core.data import FAWorkflow
from pydantic import BaseModel
from .typings_base import BaseResponse


class InspectGetWorkflowQuery(BaseModel):
    workflow_dataset: str
    workflow_id: str


class InspectGetWorkflowResponse(BaseResponse):
    workflow: FAWorkflow
    msg: str
