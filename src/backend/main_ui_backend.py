""" 
Usage::

    uvicorn main_ui_backend:app --host 0.0.0.0 --port 8100 --reload

@241208
- [x] basic implement with FastAPI

- [ ] mimic OpenAI stream API
    https://platform.openai.com/docs/api-reference/chat
    https://cookbook.openai.com/examples/how_to_stream_completions
"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio, json
from pydantic import BaseModel

from flowagent.roles import UISingleBot, RequestTool
from flowagent.data import Workflow, Config, Conversation

class BotOutput(BaseModel):
    # 根据你的实际需求定义字段
    response: str
    metadata: dict
    # ... 其他字段

class SessionContext(BaseModel):
    # Add this configuration to allow arbitrary types
    model_config = {
        "arbitrary_types_allowed": True
    }
    
    # session context, include all the necessary information
    conversation_id: str
    cfg: Config
    conv: Conversation
    workflow: Workflow
    bot: UISingleBot
    tool: RequestTool
    # user

    @classmethod
    def from_config(cls, conversation_id: str, cfg: Config):
        workflow = Workflow(cfg)
        conv = Conversation.create(conversation_id)
        bot = UISingleBot(cfg=cfg, conv=conv, workflow=workflow)
        tool = RequestTool(cfg=cfg, conv=conv, workflow=workflow)
        return cls(conversation_id=conversation_id, cfg=cfg, conv=conv, workflow=workflow, bot=bot, tool=tool)

    def merge_conversation(self, new_conv: Conversation):
        pass

SESSION_CONTEXT_MAP = {}
def get_session_context(conversation_id: str, cfg: Config=None) -> SessionContext:
    if conversation_id not in SESSION_CONTEXT_MAP:
        assert cfg is not None, "cfg is required when creating a new session context"
        SESSION_CONTEXT_MAP[conversation_id] = SessionContext.from_config(conversation_id, cfg)
    return SESSION_CONTEXT_MAP[conversation_id]



app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

def _pre_control(bot_output: BotOutput) -> None:
    """ Make pre-control on the bot's action
    will change the PDLBot's prompt! 
    """
    # if not (self.cfg.exp_mode == "session" and isinstance(self.bot, PDLBot)):  return
    for controller in ss.controllers.values():
        print(f"> [pre_control] {controller.name}")
        if not controller.if_pre_control: continue
        controller.pre_control(bot_output)

async def generate_response(session_context: SessionContext) -> AsyncGenerator[str, None]:
    print(f">> conversation: {json.dumps(str(session_context.conv), ensure_ascii=False)}")
    # TODO: pre_control
    # _pre_control(bot_output)
    
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
    final_output = {
        "is_finish": True,
        "conversation_id": session_context.conversation_id,
        "bot_output": bot_output.model_dump(),  # serialize! 
    }
    yield f"data: {json.dumps(final_output, ensure_ascii=False)}\n\n"

class SingleRegisterResponse(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }
    conversation_id: str
    success: bool
    conversation: Conversation

@app.post("/single_register/{conversation_id}")
async def single_register(conversation_id: str, config: Config) -> SingleRegisterResponse:
    print(f"> [single_register] {conversation_id} with {config}")
    session_context = get_session_context(conversation_id, cfg=config)
    return SingleRegisterResponse(
        conversation_id=conversation_id,
        success=True,
        conversation=session_context.conv
    )

@app.post("/single_bot_predict/{conversation_id}")
async def single_bot_predict(conversation_id: str, conversation: Conversation) -> StreamingResponse:
    print(f"> [single_bot_predict] {conversation_id} with {conversation}")
    session_context = get_session_context(conversation_id)
    session_context.merge_conversation(conversation)
    return StreamingResponse(
        generate_response(session_context),
        media_type="text/event-stream"
    )

@app.post("/single_post_control/{conversation_id}")
def single_post_control(bot_output: BotOutput, ) -> bool:
    """ Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to ss.conv!
    """
    for controller in ss.controllers.values():
        if not controller.if_post_control: continue
        if not controller.post_control(bot_output): return False
    return True