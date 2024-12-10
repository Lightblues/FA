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
        """init a new session with session_id & config

        Args:
            conversation_id (str): session_id
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
        conv = Conversation.create(conversation_id)
        conv.add_message(msg=cfg.ui_greeting_msg.format(name=workflow.pdl.Name), role=Role.BOT)
        bot = UISingleBot(cfg=cfg, conv=conv, workflow=workflow)
        tool = RequestTool(cfg=cfg, conv=conv, workflow=workflow)
        controllers = {}
        for c in cfg.bot_pdl_controllers:
            if c['is_activated']:
                controllers[c['name']] = CONTROLLER_NAME2CLASS[c['name']](conv, workflow.pdl, c['config'])
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
