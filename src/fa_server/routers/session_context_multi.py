"""
@241211
- [x] #feat implement MultiSessionContext
    structure:
        session_id, user_identity, cfg, conv,
        curr_status, agent_main,
        workflow_agent_map, workflow_tool_map, workflow_controllers_map,
        last_bot_output

"""

from typing import Dict, Optional, Union

from loguru import logger
from pydantic import BaseModel

from fa_core.common import Config
from fa_core.agents import CONTROLLER_NAME2CLASS, BaseController, RequestTool, UIMultiMainBot, UIMultiWorkflowBot, Context
from fa_core.data import BotOutput, Conversation, FAWorkflow

from ..common.shared import get_db


db = get_db()


class MultiSessionContext(BaseModel):
    # Add this configuration to allow arbitrary types
    model_config = {"arbitrary_types_allowed": True}

    # session context, include all the necessary information
    session_id: str
    user_identity: Optional[Dict] = None

    cfg: Config
    conv: Conversation
    curr_status: str = "main"
    # workflow: Workflow
    agent_main: UIMultiMainBot

    _workflow_agent_map: Dict[str, UIMultiWorkflowBot] = {}
    _workflow_tool_map: Dict[str, RequestTool] = {}
    _workflow_controllers_map: Dict[str, Dict[str, BaseController]] = {}

    last_bot_output: Optional[BotOutput] = None
    last_tool_output: Optional[str] = None

    @classmethod
    def from_config(cls, session_id: str, cfg: Config):
        """init a new session with session_id & config

        Args:
            session_id (str): session_id
            cfg (Config): config.
                Used config:
                    ``Workflow``: workflow_id
                        mode | exp_mode | user_mode
                    ``UISingleBot``: bot_template_fn, bot_llm_name, bot_retry_limit
                    ``RequestTool``: api_entity_linking
                        ``EntityLinker``: api_entity_linking_llm, api_entity_linking_template
                    ``controllers``: bot_pdl_controllers

        Returns:
            SessionContext: session context
        """
        data_handler = FAWorkflow.from_config(cfg)
        conv = Conversation.create(session_id)
        conv.add_message(msg=cfg.mui_greeting_msg, role="bot_main")
        _context = Context(cfg=cfg, workflow=data_handler, conv=conv)
        agent_main = UIMultiMainBot(cfg=cfg, context=_context)
        tool = RequestTool(cfg=cfg, context=_context)
        return cls(
            session_id=session_id,
            cfg=cfg,
            conv=conv,
            agent_main=agent_main,
            tool=tool,
        )

    def init_workflow_agent(self, workflow_name: str):
        if workflow_name in self._workflow_agent_map:
            assert all(
                workflow_name in m
                for m in (
                    self._workflow_agent_map,
                    self._workflow_tool_map,
                    self._workflow_controllers_map,
                )
            ), "workflow_name already exists"
            return
        else:
            assert not any(
                workflow_name in m
                for m in (
                    self._workflow_agent_map,
                    self._workflow_tool_map,
                    self._workflow_controllers_map,
                )
            ), "workflow_name already exists"
            workflow = FAWorkflow(workflow_dataset=self.cfg.workflow_dataset, workflow_id=workflow_name)
            self._workflow_agent_map[workflow_name] = UIMultiWorkflowBot(cfg=self.cfg, conv=self.conv, workflow=workflow)
            self._workflow_tool_map[workflow_name] = RequestTool(cfg=self.cfg, conv=self.conv, data_handler=workflow)
            self._workflow_controllers_map[workflow_name] = {}
            for c in self.cfg.bot_pdl_controllers:
                if c["is_activated"]:
                    self._workflow_controllers_map[workflow_name][c["name"]] = CONTROLLER_NAME2CLASS[c["name"]](self.conv, workflow.pdl, c["config"])

    @property
    def workflow_agent(self) -> UIMultiWorkflowBot:
        return self._workflow_agent_map[self.curr_status]

    @property
    def workflow_tool(self) -> RequestTool:
        return self._workflow_tool_map[self.curr_status]

    @property
    def workflow_controllers(self) -> Dict[str, BaseController]:
        return self._workflow_controllers_map[self.curr_status]


MULTI_SESSION_CONTEXT_MAP = {}


def create_session_context(session_id: str, cfg: Config) -> MultiSessionContext:
    assert session_id not in MULTI_SESSION_CONTEXT_MAP, "session_id already exists"
    session_context = MultiSessionContext.from_config(session_id, cfg)
    MULTI_SESSION_CONTEXT_MAP[session_id] = session_context
    return session_context


def get_session_context_multi(session_id: str) -> Union[MultiSessionContext, None]:
    if session_id not in MULTI_SESSION_CONTEXT_MAP:
        return None
    return MULTI_SESSION_CONTEXT_MAP[session_id]


def clear_session_context_multi(session_id: str):
    """Clear the session context"""
    if session_id in MULTI_SESSION_CONTEXT_MAP:
        del MULTI_SESSION_CONTEXT_MAP[session_id]


def db_upsert_session_multi(ss: MultiSessionContext):
    """Upsert conversation to `cfg.db_collection_multi`
    Infos: (sessionid, name, mode[multi/multi], infos, conversation, version)...

    NOTE:
    - ideal upsert time? -> multi_disconnect
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
        "mode": "multi",
        "conversation": ss.conv.to_list(),  # TODO: only save messages? polish it!
        "config": ss.cfg.model_dump(),  # to_list -> model_dump
        # "workflow": ss.workflow.model_dump(),
    }
    if db is None:
        logger.warning(f"Skipping database operation for session {ss.session_id} due to connection failure")
        return
    try:
        db[ss.cfg.db_collection_multi].replace_one({"session_id": ss.session_id}, _session_info, upsert=True)
    except Exception as e:
        logger.error(f"Failed to save session {ss.session_id}: {e}")


def clear_session_contexts_multi():
    """Clear all the session contexts:
    - save the conversation to db
    - clear the session context cache
    """
    # Create a list of session IDs first to avoid modifying dict during iteration
    session_ids = list(MULTI_SESSION_CONTEXT_MAP.keys())
    logger.warning(f"[clear_session_contexts] clearing session_ids: {session_ids}")

    for session_id in session_ids:
        session_context = MULTI_SESSION_CONTEXT_MAP.get(session_id)
        if session_context:
            db_upsert_session_multi(session_context)
            clear_session_context_multi(session_id)
