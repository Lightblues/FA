from pydantic import BaseModel
from typing import Optional, Union, Dict
from flowagent.roles import UISingleBot, RequestTool
from flowagent.pdl_controllers import CONTROLLER_NAME2CLASS, BaseController
from flowagent.data import Workflow, Config, Conversation, BotOutput, Message, Role

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
    controllers: Dict[str, BaseController]
    # user
    last_bot_output: Optional[BotOutput] = None

    @classmethod
    def from_config(cls, conversation_id: str, cfg: Config):
        workflow = Workflow(cfg)
        conv = Conversation.create(conversation_id)
        bot = UISingleBot(cfg=cfg, conv=conv, workflow=workflow)
        tool = RequestTool(cfg=cfg, conv=conv, workflow=workflow)
        controllers = {c['name']: CONTROLLER_NAME2CLASS[c['name']](conv, workflow.pdl, c['config']) for c in cfg.bot_pdl_controllers}
        return cls(conversation_id=conversation_id, cfg=cfg, conv=conv, workflow=workflow, bot=bot, tool=tool, controllers=controllers)

    def merge_conversation(self, new_conv: Conversation):
        self.conv.msgs = new_conv.msgs

    def _add_message(self, msg_content: str, prompt: str=None, llm_response:str=None, role:Union[Role, str]=Role.USER):
        msg = Message(
            role=role, content=msg_content, prompt=prompt, llm_response=llm_response,
            conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
        )
        self.conv.add_message(msg)

SESSION_CONTEXT_MAP = {}
def get_session_context(conversation_id: str, cfg: Config=None) -> SessionContext:
    if conversation_id not in SESSION_CONTEXT_MAP:
        assert cfg is not None, "cfg is required when creating a new session context"
        SESSION_CONTEXT_MAP[conversation_id] = SessionContext.from_config(conversation_id, cfg)
    return SESSION_CONTEXT_MAP[conversation_id]
