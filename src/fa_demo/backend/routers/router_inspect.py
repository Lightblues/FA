from fastapi import APIRouter
from loguru import logger

from fa_core.common import log_exceptions, json_line
from fa_core.data import FAWorkflow
from fa_demo.backend.typings import InspectGetWorkflowQuery, InspectGetWorkflowResponse

router_inspect = APIRouter()


@router_inspect.get("/inspect_get_workflow/{conversation_id}")
@log_exceptions()  # NOTE: MUST use `@log_exceptions()` before `@router_single.post()` to catch the exception!
async def inspect_get_workflow(conversation_id: str, request: InspectGetWorkflowQuery) -> InspectGetWorkflowResponse:
    logger.info(f"<{conversation_id}> [inspect_get_workflow] ...")
    workflow = FAWorkflow(workflow_dataset=request.workflow_dataset, workflow_id=request.workflow_id)
    return InspectGetWorkflowResponse(workflow=workflow, msg="")
