"""APIs for single-agent
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
- [x] #api `/single_disconnect/` to clear the session context

- [ ] purify the doc
"""

import json
from typing import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger

from data import Message
from common import log_exceptions

from ..typings import (
    BotOutput,
    SingleBotPredictResponse,
    SinglePostControlResponse,
    SingleRegisterRequest,
    SingleRegisterResponse,
    SingleToolResponse,
)
from .session_context_single import (
    SingleSessionContext,
    clear_session_context_single,
    create_session_context_single,
    db_upsert_session_single,
    get_session_context_single,
)


# TODO: wrap the pre_control to a API?
def _pre_control(session_context: SingleSessionContext) -> None:
    """Make pre-control on the bot's action
    will change the PDLBot's prompt!
    """
    # if not (self.cfg.exp_mode == "session" and isinstance(self.bot, PDLBot)):  return
    for controller in session_context.controllers.values():
        if not controller.if_pre_control:
            continue
        # print(f"> [pre_control] {controller.name}")
        controller.pre_control(session_context.last_bot_output)


def generate_response(session_context: SingleSessionContext) -> Iterator[str]:
    logger.info(f">>> model={session_context.bot.llm.model} conversation={json.dumps(str(session_context.conv), ensure_ascii=False)}")
    _pre_control(session_context)

    stream = session_context.bot.process_stream()
    for chunk in stream:
        chunk_output = {
            "is_finish": False,
            "conversation_id": session_context.session_id,
            "chunk": chunk,
        }
        yield f"data: {json.dumps(chunk_output, ensure_ascii=False)}\n\n"
    bot_output = session_context.bot.process_LLM_response()
    _debug_msg = f"\n{f'({session_context.session_id}) [BOT] ({session_context.workflow.name}) ({session_context.bot.llm.model})'.center(50, '=')}\n<<lllm prompt>>\n{session_context.bot.last_llm_prompt}\n\n<<llm response>>\n{session_context.bot.last_llm_response}\n"
    logger.bind(custom=True).debug(_debug_msg)
    session_context.last_bot_output = bot_output
    logger.info(f"<{session_context.session_id}> [generate_response] done!")


router_single = APIRouter()


@log_exceptions()
@router_single.post("/single_register/{conversation_id}")
async def single_register(conversation_id: str, request: SingleRegisterRequest) -> SingleRegisterResponse:
    """init a new session with session_id & config

    Args:
        conversation_id (str): session_id
        config (SingleRegisterRequest): config

    Returns:
        SingleRegisterResponse: with conversation
    """
    logger.info(f"<{conversation_id}> [single_register] creating session context...")
    session_context = create_session_context_single(conversation_id, cfg=request.config)
    session_context.user_identity = request.user_identity
    response = SingleRegisterResponse(
        conversation_id=conversation_id,
        success=True,
        conversation=session_context.conv,
        pdl_str=session_context.workflow.pdl.to_str(),
    )
    logger.info(f"<{conversation_id}> [single_register] done!")
    return response


@log_exceptions()
@router_single.post("/single_disconnect/{conversation_id}")
def single_disconnect(conversation_id: str) -> None:
    """Disconnect the session"""
    logger.info(f"<{conversation_id}> [single_disconnect] clearing session context...")
    db_upsert_session_single(get_session_context_single(conversation_id))
    clear_session_context_single(conversation_id)
    logger.info(f"<{conversation_id}> [single_disconnect] done!")


@log_exceptions()
@router_single.post("/single_add_message/{conversation_id}")
def single_add_message(conversation_id: str, message: Message) -> None:
    logger.info(f"<{conversation_id}> [single_add_message] adding message: {message}")
    session_context = get_session_context_single(conversation_id)
    session_context.conv.add_message(message)
    logger.info(f"<{conversation_id}> [single_add_message] done!")


@log_exceptions()
@router_single.post("/single_bot_predict/{conversation_id}")
async def single_bot_predict(conversation_id: str) -> StreamingResponse:
    logger.info(f"<{conversation_id}> [single_bot_predict] predicting...")
    session_context = get_session_context_single(conversation_id)
    return StreamingResponse(generate_response(session_context), media_type="text/event-stream")


@log_exceptions()
@router_single.get("/single_bot_predict_output/{conversation_id}")
def single_bot_predict_output(conversation_id: str) -> SingleBotPredictResponse:
    logger.info(f"<{conversation_id}> [single_bot_predict_output] getting bot output...")
    session_context = get_session_context_single(conversation_id)
    response = SingleBotPredictResponse(
        bot_output=session_context.last_bot_output,
        msg=session_context.conv.get_last_message().content,
    )
    logger.info(f"<{conversation_id}> [single_bot_predict_output] done! response: {response.bot_output}")
    return response


@log_exceptions()
@router_single.post("/single_post_control/{conversation_id}")
def single_post_control(conversation_id: str, bot_output: BotOutput) -> SinglePostControlResponse:
    """Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to ss.conv!
    """
    session_context = get_session_context_single(conversation_id)
    logger.info(f"<{conversation_id}> [single_post_control] checking post control with controllers: {session_context.controllers.keys()}...")
    success = True
    for controller in session_context.controllers.values():
        if not controller.if_post_control:
            continue
        if not controller.post_control(bot_output):
            success = False
            break
    response = SinglePostControlResponse(
        success=success,
        msg="" if success else session_context.conv.get_last_message().content,  # TODO: format the error message
    )
    logger.info(f"<{conversation_id}> [single_post_control] done! response: {response}")
    return response


@log_exceptions()
@router_single.post("/single_tool/{conversation_id}")
def single_tool(conversation_id: str, bot_output: BotOutput) -> SingleToolResponse:
    logger.info(f"<{conversation_id}> [single_tool] calling tool with bot_output: {bot_output}")
    session_context = get_session_context_single(conversation_id)
    api_output = session_context.tool.process(bot_output)
    _debug_msg = f"\n{f'({session_context.session_id}) [API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    logger.bind(custom=True).debug(_debug_msg)
    response = SingleToolResponse(api_output=api_output, msg=session_context.conv.get_last_message().content)
    logger.info(f"<{conversation_id}> [single_tool] done! response: {response.api_output}")
    return response
