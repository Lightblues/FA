

""" APIs for single-agent
Test: see `test/backend/test_ui_backend.py`

@241210
- [x] implement single-agent APIs:
    - [x] single_register
    - [x] single_bot_predict
    - [x] single_post_control
    - [x] single_tool
- [x] pre_control

- [ ] add logging to db! 
"""
import json
from typing import Iterator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..session_context import get_session_context, SessionContext
from ..typings import (
    SingleRegisterRequest, SingleRegisterResponse, 
    SingleBotPredictRequest, SingleBotPredictResponse, 
    SinglePostControlResponse, 
    SingleToolResponse
)

router = APIRouter()


@router.post("/single_register/{conversation_id}")
async def single_register(conversation_id: str, config: SingleRegisterRequest) -> SingleRegisterResponse:
    print(f"> [single_register] {conversation_id}")
    session_context = get_session_context(conversation_id, cfg=config)
    return SingleRegisterResponse(
        conversation_id=conversation_id,
        success=True,
        conversation=session_context.conv
    )


# TODO: wrap the pre_control to a API?
def _pre_control(session_context: SessionContext) -> None:
    """ Make pre-control on the bot's action
    will change the PDLBot's prompt! 
    """
    # if not (self.cfg.exp_mode == "session" and isinstance(self.bot, PDLBot)):  return
    for controller in session_context.controllers.values():
        if not controller.if_pre_control: continue
        print(f"> [pre_control] {controller.name}")
        controller.pre_control(session_context.last_bot_output)


def generate_response(session_context: SessionContext) -> Iterator[str]:
    print(f">> generate_response with conversation: {json.dumps(str(session_context.conv), ensure_ascii=False)}")
    _pre_control(session_context)
    
    prompt, stream = session_context.bot.process_stream()  # TODO: ReactBot -> PDL_UIBot
    llm_response = []
    for chunk in stream:
        llm_response.append(chunk)
        chunk_output = {
            "is_finish": False,
            "conversation_id": session_context.conversation_id,
            "chunk": chunk
        }
        yield f"data: {json.dumps(chunk_output, ensure_ascii=False)}\n\n"
    llm_response = "".join(llm_response)
    bot_output = session_context.bot.process_LLM_response(prompt, llm_response)
    # final_output = {
    #     "is_finish": True,
    #     "conversation_id": session_context.conversation_id,
    #     "bot_output": bot_output.model_dump(),  # serialize! 
    # }
    # yield f"data: {json.dumps(final_output, ensure_ascii=False)}\n\n"
    session_context.last_bot_output = bot_output

@router.post("/single_bot_predict/{conversation_id}")
async def single_bot_predict(conversation_id: str, request: SingleBotPredictRequest) -> StreamingResponse:
    print(f"> [single_bot_predict] {conversation_id} with query: {request.query}")
    session_context = get_session_context(conversation_id)
    session_context._add_message(request.query)     # add user query
    return StreamingResponse(
        generate_response(session_context),
        media_type="text/event-stream"
    )

@router.get("/single_bot_predict_output/{conversation_id}")
def single_bot_predict_output(conversation_id: str) -> SingleBotPredictResponse:
    session_context = get_session_context(conversation_id)
    return session_context.last_bot_output

@router.post("/single_post_control/{conversation_id}")
def single_post_control(conversation_id: str, bot_output: SingleBotPredictResponse) -> SinglePostControlResponse:
    """ Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to ss.conv!
    """
    session_context = get_session_context(conversation_id)
    success = True
    for controller in session_context.controllers.values():
        if not controller.if_post_control: continue
        if not controller.post_control(bot_output):
            success = False
            break
    return SinglePostControlResponse(
        success=success,
        content=session_context.conv.get_last_message().to_str() # TODO: format the error message
    )

@router.post("/single_tool/{conversation_id}")
def single_tool(conversation_id: str, bot_output: SingleBotPredictResponse) -> SingleToolResponse:
    print(f"> [single_tool] {conversation_id} with bot_output: {bot_output}")
    session_context = get_session_context(conversation_id)
    return session_context.tool.process(bot_output)
