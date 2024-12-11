

""" APIs for single-agent
Test: see `test/backend/test_ui_backend.py`

@241210
- [x] implement single-agent APIs:
    - [x] single_register
    - [x] single_bot_predict
    - [x] single_post_control
    - [x] single_tool
- [x] pre_control
@241211
- [x] #log add record to db! 
    `db_upsert_session`
- [x] #log add log / debug
- [x] #api /single_disconnect/ to clear the session context

- [ ] purify the doc
"""
import json, pymongo
from typing import Iterator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from .session_context import create_session_context, get_session_context, clear_session_context, SessionContext, SESSION_CONTEXT_MAP
from flowagent.data import Role, Message
from ..typings import (
    SingleRegisterRequest, SingleRegisterResponse, 
    SingleBotPredictResponse, 
    SinglePostControlResponse, 
    SingleToolResponse, BotOutput
)
from ..common.shared import get_db, get_logger
logger = get_logger()
db = get_db()

def db_upsert_session(ss: SessionContext):
    """Upsert conversation to `db.backend_single_sessions`
    Infos: (sessionid, name, mode[single/multi], infos, conversation, version)...

    NOTE: 
    - ideal upsert time? -> single_disconnect
    - save the conversation to db when user exit the page
    """
    # only save conversation when user has queried
    if (not ss) or (len(ss.conv) <= 1):
        return
    logger.info(f"[db_upsert_session] {ss.session_id}")
    _session_info = {
        # model_llm_name, template, etc
        "session_id": ss.session_id,
        "user": ss.user_identity,
        "mode": "single",
        "conversation": ss.conv.to_list(), # TODO: only save messages? polish it!
        "config": ss.cfg.model_dump(),      # to_list -> model_dump
    }
    db.backend_single_sessions.replace_one(
        {"session_id": ss.session_id},
        _session_info,
        upsert=True
    )

def clear_session_contexts():
    """Clear all the session contexts:
    - save the conversation to db
    - clear the session context cache
    """
    # Create a list of session IDs first to avoid modifying dict during iteration
    session_ids = list(SESSION_CONTEXT_MAP.keys())
    logger.warning(f"[clear_session_contexts] clearing session_ids: {session_ids}")
    
    for session_id in session_ids:
        session_context = SESSION_CONTEXT_MAP.get(session_id)
        if session_context:
            db_upsert_session(session_context)
            clear_session_context(session_id)

router_single = APIRouter()

@router_single.post("/single_register/{conversation_id}")
async def single_register(conversation_id: str, request: SingleRegisterRequest) -> SingleRegisterResponse:
    """init a new session with session_id & config

    Args:
        conversation_id (str): session_id
        config (SingleRegisterRequest): config

    Returns:
        SingleRegisterResponse: with conversation
    """
    logger.info(f"[single_register] {conversation_id}")
    session_context = create_session_context(conversation_id, cfg=request.config)
    session_context.user_identity = request.user_identity
    return SingleRegisterResponse(
        conversation_id=conversation_id,
        success=True,
        conversation=session_context.conv,
        pdl_str=session_context.workflow.pdl.to_str()
    )

@router_single.post("/single_disconnect/{conversation_id}")
def single_disconnect(conversation_id: str) -> None:
    """Disconnect the session
    """
    logger.info(f"[single_disconnect] {conversation_id}")
    db_upsert_session(get_session_context(conversation_id))
    clear_session_context(conversation_id)

# TODO: wrap the pre_control to a API?
def _pre_control(session_context: SessionContext) -> None:
    """ Make pre-control on the bot's action
    will change the PDLBot's prompt! 
    """
    # if not (self.cfg.exp_mode == "session" and isinstance(self.bot, PDLBot)):  return
    for controller in session_context.controllers.values():
        if not controller.if_pre_control: continue
        # print(f"> [pre_control] {controller.name}")
        controller.pre_control(session_context.last_bot_output)


def generate_response(session_context: SessionContext) -> Iterator[str]:
    logger.info(f">> generate_response with conversation: {json.dumps(str(session_context.conv), ensure_ascii=False)}")
    _pre_control(session_context)
    
    prompt, stream = session_context.bot.process_stream()  # TODO: ReactBot -> PDL_UIBot
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
    bot_output = session_context.bot.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    logger.bind(custom=True).debug(_debug_msg)
    session_context.last_bot_output = bot_output

@router_single.post("/single_add_message/{conversation_id}")
def single_add_message(conversation_id: str, message: Message) -> None:
    logger.info(f"[single_add_message] {conversation_id} with message: {message}")
    session_context = get_session_context(conversation_id)
    session_context.conv.add_message(message)

@router_single.post("/single_bot_predict/{conversation_id}")
async def single_bot_predict(conversation_id: str) -> StreamingResponse:
    logger.info(f"[single_bot_predict] {conversation_id}")
    session_context = get_session_context(conversation_id)
    # db_upsert_session(session_context)
    return StreamingResponse(
        generate_response(session_context),
        media_type="text/event-stream"
    )

@router_single.get("/single_bot_predict_output/{conversation_id}")
def single_bot_predict_output(conversation_id: str) -> SingleBotPredictResponse:
    logger.info(f"[single_bot_predict_output] {conversation_id}")
    session_context = get_session_context(conversation_id)
    # db_upsert_session(session_context)
    return SingleBotPredictResponse(
        bot_output=session_context.last_bot_output,
        msg=session_context.conv.get_last_message().content
    )

@router_single.post("/single_post_control/{conversation_id}")
def single_post_control(conversation_id: str, bot_output: BotOutput) -> SinglePostControlResponse:
    """ Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to ss.conv!
    """
    logger.info(f"[single_post_control] {conversation_id} with bot_output: {bot_output}")
    session_context = get_session_context(conversation_id)
    success = True
    for controller in session_context.controllers.values():
        if not controller.if_post_control: continue
        if not controller.post_control(bot_output):
            success = False
            break
    # db_upsert_session(session_context)
    return SinglePostControlResponse(
        success=success,
        msg="" if success else session_context.conv.get_last_message().content # TODO: format the error message
    )

@router_single.post("/single_tool/{conversation_id}")
def single_tool(conversation_id: str, bot_output: BotOutput) -> SingleToolResponse:
    logger.info(f"[single_tool] {conversation_id} with bot_output: {bot_output}")
    session_context = get_session_context(conversation_id)
    api_output = session_context.tool.process(bot_output)
    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    logger.bind(custom=True).debug(_debug_msg)
    # db_upsert_session(session_context)
    return SingleToolResponse(
        api_output=api_output,
        msg=session_context.conv.get_last_message().content
    )
