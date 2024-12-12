""" 
@241210
- [x] #feat implement SingleSessionContext
    structure: session_id, user_identity, cfg, conv, workflow, bot, tool, controllers, last_bot_output
@241211
- [x] #feat upload to db before shutdown:  `clear_session_contexts_single`
- [x] #structure seperate single & multi SessionContext
"""

from pydantic import BaseModel
from typing import Optional, Union, Dict
from flowagent.roles import UISingleBot, RequestTool
from flowagent.pdl_controllers import CONTROLLER_NAME2CLASS, BaseController
from flowagent.data import Workflow, Config, Conversation, BotOutput, Role

from ..common.shared import get_db, get_logger
logger = get_logger()
db = get_db()

class SingleSessionContext(BaseModel):
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
        # logger.info(f"cfg.bot_pdl_controllers: {cfg.bot_pdl_controllers}")
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


SINGLE_SESSION_CONTEXT_MAP = {}
def create_session_context_single(session_id: str, cfg: Config) -> SingleSessionContext:
    assert session_id not in SINGLE_SESSION_CONTEXT_MAP, "session_id already exists"
    session_context = SingleSessionContext.from_config(session_id, cfg)
    SINGLE_SESSION_CONTEXT_MAP[session_id] = session_context
    return session_context

def get_session_context_single(session_id: str) -> Union[SingleSessionContext, None]:
    if session_id not in SINGLE_SESSION_CONTEXT_MAP: return None
    return SINGLE_SESSION_CONTEXT_MAP[session_id]

def clear_session_context_single(session_id: str):
    """Clear the session context
    """
    if session_id in SINGLE_SESSION_CONTEXT_MAP:
        del SINGLE_SESSION_CONTEXT_MAP[session_id]



def db_upsert_session_single(ss: SingleSessionContext):
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

def clear_session_contexts_single():
    """Clear all the session contexts:
    - save the conversation to db
    - clear the session context cache
    """
    # Create a list of session IDs first to avoid modifying dict during iteration
    session_ids = list(SINGLE_SESSION_CONTEXT_MAP.keys())
    logger.warning(f"[clear_session_contexts_single] clearing session_ids: {session_ids}")
    
    for session_id in session_ids:
        session_context = SINGLE_SESSION_CONTEXT_MAP.get(session_id)
        if session_context:
            db_upsert_session_single(session_context)
            clear_session_context_single(session_id)