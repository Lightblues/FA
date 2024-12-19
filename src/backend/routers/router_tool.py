"""
@241212
- [x] #feat add tool main & stream
    /multi_tool_main_stream, /multi_tool_main_output
- [x] #feat add error_handling
    in API level? NOTE: can it be abstracted?
"""

import json
from typing import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger

from tools import execute_tool_call

from ..typings import MainBotOutput, MultiToolMainResponse
from .session_context_multi import get_session_context_multi


router_tool = APIRouter()


@router_tool.post("/multi_tool_main/{conversation_id}")
def multi_tool_main(conversation_id: str, bot_output: MainBotOutput) -> MultiToolMainResponse:
    logger.info(f"[multi_tool_main] {conversation_id} with bot_output: {bot_output}")
    try:
        session_context = get_session_context_multi(conversation_id)
        res = execute_tool_call(bot_output.action, bot_output.action_input)
        if isinstance(res, Iterator):
            res = "".join(res)
        res = json.dumps(res, ensure_ascii=False)  # NOTE dump into a line
        session_context.conv.add_message(res, role="tool")  # TODO: manage the rolename with config
        return MultiToolMainResponse(tool_output=res, msg=session_context.conv.get_last_message())
    except Exception as e:
        return MultiToolMainResponse(error_code=1, error_msg=str(e))


@router_tool.post("/multi_tool_main_stream/{conversation_id}")
def multi_tool_main_stream(conversation_id: str, bot_output: MainBotOutput) -> StreamingResponse:
    """Streaming response for the tool main

    NOTE:
    - the tool output is not a string, but a stream of data
    - add the complete response to the conversation
    """
    logger.info(f"[multi_tool_main_stream] {conversation_id} with bot_output: {bot_output}")
    session_context = get_session_context_multi(conversation_id)

    def generate_tool_response():
        res = execute_tool_call(bot_output.action, bot_output.action_input)
        if isinstance(res, str):
            res = json.dumps(res, ensure_ascii=False)
            chunk_output = {
                "is_finish": True,
                "conversation_id": conversation_id,
                "chunk": res,
            }
            yield f"data: {json.dumps(chunk_output, ensure_ascii=False)}\n\n"
            session_context.last_tool_output = res
            session_context.conv.add_message(res, role="tool")  # TODO: purify the tool message?
        elif isinstance(res, Iterator):
            full_response = []
            for chunk in res:
                full_response.append(chunk)
                chunk_output = {
                    "is_finish": False,
                    "conversation_id": conversation_id,
                    "chunk": chunk,
                }
                yield f"data: {json.dumps(chunk_output, ensure_ascii=False)}\n\n"
            res = "".join(full_response)
            res = json.dumps(res, ensure_ascii=False)
            session_context.last_tool_output = res
            session_context.conv.add_message(res, role="tool")
        else:
            raise ValueError(f"Unsupported tool output type: {type(res)}")

    return StreamingResponse(generate_tool_response(), media_type="text/event-stream")


@router_tool.get("/multi_tool_main_output/{conversation_id}")
def multi_tool_main_output(conversation_id: str) -> MultiToolMainResponse:
    session_context = get_session_context_multi(conversation_id)
    return MultiToolMainResponse(
        tool_output=session_context.last_tool_output,
        msg=session_context.conv.get_last_message(),
    )
