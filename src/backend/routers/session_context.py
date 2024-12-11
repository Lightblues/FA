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
    session_id: str
    user_identity: Optional[Dict] = None

    cfg: Config
    conv: Conversation
    workflow: Workflow
    bot: UISingleBot
    tool: RequestTool
    controllers: Dict[str, BaseController]
    # user
    last_bot_output: Optional[BotOutput] = None

    @classmethod
    def from_config(cls, session_id: str, cfg: Config):
        """init a new session with session_id & config

        Args:
            session_id (str): session_id
            cfg (Config): config. 
                Used config:
                    ``Workflow``: workflow_type, workflow_id, pdl_version
                        mode | exp_mode | user_mode
                    ``UISingleBot``: ui_bot_template_fn, bot_llm_name, bot_retry_limit
                    ``RequestTool``: api_entity_linking
                        ``EntityLinker``: api_entity_linking_llm, api_entity_linking_template
                    ``controllers``: bot_pdl_controllers

        Returns:
            SessionContext: session context
        """
        workflow = Workflow(cfg)
        conv = Conversation.create(session_id)
        conv.add_message(msg=cfg.ui_greeting_msg.format(name=workflow.pdl.Name), role=Role.BOT)
        bot = UISingleBot(cfg=cfg, conv=conv, workflow=workflow)
        tool = RequestTool(cfg=cfg, conv=conv, workflow=workflow)
        controllers = {}
        for c in cfg.bot_pdl_controllers:
            if c['is_activated']:
                controllers[c['name']] = CONTROLLER_NAME2CLASS[c['name']](conv, workflow.pdl, c['config'])
        return cls(session_id=session_id, cfg=cfg, conv=conv, workflow=workflow, bot=bot, tool=tool, controllers=controllers)

    def merge_conversation(self, new_conv: Conversation):
        self.conv.msgs = new_conv.msgs


SESSION_CONTEXT_MAP = {}
def get_session_context(session_id: str, cfg: Config=None) -> SessionContext:
    if session_id not in SESSION_CONTEXT_MAP:
        assert cfg is not None, "cfg is required when creating a new session context"
        session_context = SessionContext.from_config(session_id, cfg)
        SESSION_CONTEXT_MAP[session_id] = session_context
    return SESSION_CONTEXT_MAP[session_id]

def clear_session_context(session_id: str):
    """Clear the session context
    """
    if session_id in SESSION_CONTEXT_MAP:
        del SESSION_CONTEXT_MAP[session_id]
