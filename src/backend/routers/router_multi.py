""" APIs for multi-agent
Test: see `test/backend/test_ui_backend_multi.py`

@241211
- [x] #feat implement multi-agent APIs
    API: 
        multi_register, multi_disconnect, multi_add_message,
        multi_bot_main_predict, multi_bot_main_predict_output, multi_tool_main, 
        multi_bot_workflow_predict, multi_bot_workflow_predict_output,
        multi_post_control, multi_tool_workflow

- [ ] purify the doc
"""
import json
from typing import Iterator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from .session_context_multi import (
    create_session_context, get_session_context_multi, clear_session_context_multi, MultiSessionContext, MULTI_SESSION_CONTEXT_MAP,
    db_upsert_session_multi
)
from flowagent.data import Role, Message
from flowagent.tools import execute_tool_call
from ..typings import (
    MultiRegisterRequest, MultiRegisterResponse,
    MultiBotMainPredictResponse, MainBotOutput, 
    MultiToolMainResponse, 
    MultiBotWorkflowPredictResponse, MultiPostControlResponse, MultiToolWorkflowResponse,
    BotOutput
)
from ..common.shared import get_logger
logger = get_logger()


def generate_response_main(session_context: MultiSessionContext) -> Iterator[str]:
    logger.info(f">> [generate_response_main] with conversation: {json.dumps(str(session_context.conv), ensure_ascii=False)}")
    
    prompt, stream = session_context.agent_main.process_stream()
    llm_response = []
    for chunk in stream:
        llm_response.append(chunk)
        chunk_output = {
            "is_finish": False,
            "conversation_id": session_context.session_id,
            "chunk": chunk
        }
        yield f"data: {json.dumps(chunk_output, ensure_ascii=False)}\n\n"
    llm_response = "".join(llm_response)
    bot_output = session_context.agent_main.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'({session_context.session_id}) [BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    logger.bind(custom=True).debug(_debug_msg)
    session_context.last_bot_output = bot_output
    # NOTE: if switched to a workflow, set curr_status & init the workflow agent!
    if bot_output.workflow:
        session_context.curr_status = bot_output.workflow
        session_context.init_workflow_agent(session_context.curr_status)

# TODO: wrap the pre_control to a API?
def _pre_control(session_context: MultiSessionContext) -> None:
    """ Make pre-control on the bot's action
    will change the PDLBot's prompt! 
    """
    for controller in session_context.workflow_controllers.values():
        if not controller.if_pre_control: continue
        controller.pre_control(session_context.last_bot_output)


def generate_response_workflow(session_context: MultiSessionContext) -> Iterator[str]:
    logger.info(f">> [generate_response_workflow] with conversation: {json.dumps(str(session_context.conv), ensure_ascii=False)}")
    _pre_control(session_context)
    
    prompt, stream = session_context.workflow_agent.process_stream()
    llm_response = []
    for chunk in stream:
        llm_response.append(chunk)
        chunk_output = {
            "is_finish": False,
            "conversation_id": session_context.session_id,
            "chunk": chunk
        }
        yield f"data: {json.dumps(chunk_output, ensure_ascii=False)}\n\n"
    llm_response = "".join(llm_response)
    bot_output = session_context.workflow_agent.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'({session_context.session_id}) [BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    logger.bind(custom=True).debug(_debug_msg)
    session_context.last_bot_output = bot_output
    # NOTE: set curr_status if switched
    if bot_output.workflow: # TODO: switch to another workflow? #feat
        session_context.curr_status = "main"



router_multi = APIRouter()

@router_multi.post("/multi_register/{conversation_id}")
async def multi_register(conversation_id: str, request: MultiRegisterRequest) -> MultiRegisterResponse:
    """init a new session with session_id & config

    Args:
        conversation_id (str): session_id
        config (MultiRegisterRequest): config

    Returns:
        MultiRegisterResponse: with conversation
    """
    logger.info(f"[multi_register] {conversation_id}")
    session_context = create_session_context(conversation_id, cfg=request.config)
    session_context.user_identity = request.user_identity
    return MultiRegisterResponse(
        conversation_id=conversation_id,
        success=True,
        conversation=session_context.conv.model_dump(),
    )

@router_multi.post("/multi_disconnect/{conversation_id}")
def multi_disconnect(conversation_id: str) -> None:
    """Disconnect the session
    """
    logger.info(f"[multi_disconnect] {conversation_id}")
    db_upsert_session_multi(get_session_context_multi(conversation_id))
    clear_session_context_multi(conversation_id)

# ---
@router_multi.post("/multi_add_message/{conversation_id}")
def multi_add_message(conversation_id: str, message: Message) -> None:
    logger.info(f"[multi_add_message] {conversation_id} with message: {message}")
    session_context = get_session_context_multi(conversation_id)
    session_context.conv.add_message(message)

@router_multi.post("/multi_bot_main_predict/{conversation_id}")
async def multi_bot_main_predict(conversation_id: str) -> StreamingResponse:
    logger.info(f"[multi_bot_main_predict] {conversation_id}")
    session_context = get_session_context_multi(conversation_id)
    # db_upsert_session(session_context)
    return StreamingResponse(
        generate_response_main(session_context),
        media_type="text/event-stream"
    )

# ---
@router_multi.post("/multi_tool_main/{conversation_id}")
def multi_tool_main(conversation_id: str, bot_output: MainBotOutput) -> MultiToolMainResponse:
    logger.info(f"[multi_tool_main] {conversation_id} with bot_output: {bot_output}")
    session_context = get_session_context_multi(conversation_id)
    # simply exec 
    res = execute_tool_call(bot_output.action, bot_output.action_input)
    session_context.conv.add_message(res, role="tool")  # TODO: manage the rolename with config
    return MultiToolMainResponse(
        tool_output=res,
        msg=session_context.conv.get_last_message()
    )


# ---
@router_multi.get("/multi_bot_main_predict_output/{conversation_id}")
def multi_bot_main_predict_output(conversation_id: str) -> MultiBotMainPredictResponse:
    logger.info(f"[multi_bot_main_predict_output] {conversation_id}")
    session_context = get_session_context_multi(conversation_id)
    # db_upsert_session(session_context)
    return MultiBotMainPredictResponse(
        bot_output=session_context.last_bot_output,
        msg=session_context.conv.get_last_message()
    )

@router_multi.post("/multi_bot_workflow_predict/{conversation_id}")
async def multi_bot_workflow_predict(conversation_id: str) -> StreamingResponse:
    logger.info(f"[multi_bot_workflow_predict] {conversation_id}")
    session_context = get_session_context_multi(conversation_id)
    # db_upsert_session(session_context)
    return StreamingResponse(
        generate_response_workflow(session_context),
        media_type="text/event-stream"
    )

@router_multi.get("/multi_bot_workflow_predict_output/{conversation_id}")
def multi_bot_workflow_predict_output(conversation_id: str) -> MultiBotWorkflowPredictResponse:
    logger.info(f"[multi_bot_workflow_predict_output] {conversation_id}")
    session_context = get_session_context_multi(conversation_id)
    # db_upsert_session(session_context)
    return MultiBotWorkflowPredictResponse(
        bot_output=session_context.last_bot_output,
        msg=session_context.conv.get_last_message()
    )

@router_multi.post("/multi_post_control/{conversation_id}")
def multi_post_control(conversation_id: str, bot_output: BotOutput) -> MultiPostControlResponse:
    """ Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to ss.conv!
    """
    logger.info(f"[multi_post_control] {conversation_id} with bot_output: {bot_output}")
    session_context = get_session_context_multi(conversation_id)
    success = True
    for controller in session_context.workflow_controllers.values():
        if not controller.if_post_control: continue
        if not controller.post_control(bot_output):
            success = False
            break
    # db_upsert_session(session_context)
    return MultiPostControlResponse(
        success=success,
        msg=None if success else session_context.conv.get_last_message() # TODO: format the error message
    )

@router_multi.post("/multi_tool_workflow/{conversation_id}")
def multi_tool_workflow(conversation_id: str, bot_output: BotOutput) -> MultiToolWorkflowResponse:
    logger.info(f"[multi_tool_workflow] {conversation_id} with bot_output: {bot_output}")
    session_context = get_session_context_multi(conversation_id)
    api_output = session_context.workflow_tool.process(bot_output)
    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    logger.bind(custom=True).debug(_debug_msg)
    # db_upsert_session(session_context)
    return MultiToolWorkflowResponse(
        api_output=api_output,
        msg=session_context.conv.get_last_message()
    )