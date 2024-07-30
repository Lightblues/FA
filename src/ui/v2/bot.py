""" 
@240718 从 engine_v1.bots 进行修改
"""

import datetime
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from engine_v2 import (
    BaseLogger, Logger, PDL, BaseRole, Config, 
    Role, Message, Conversation, ConversationInfos, ActionType, 
    init_client, LLM_CFG
)
from utils.jinja_templates import jinja_render

class PDL_UIBot(BaseRole):
    llm: OpenAIClient = None
    cfg: Config = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.model_name])

    def process_stream(self, conversation: Conversation, pdl: PDL, conversation_infos: Optional[ConversationInfos] = None):
        s_current_state = None
        user_additional_constraints = None
        if conversation_infos:
            s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."
            user_additional_constraints = conversation_infos.user_additional_constraints
        head_info = f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d (%A) %H:%M:%S')}"
        prompt = jinja_render(
            self.cfg.template_fn,       # "query_PDL.jinja"
            head_info=head_info,
            conversation=conversation.to_str(), 
            PDL=pdl.to_str(),
            current_state=s_current_state,
            user_additional_constraints=user_additional_constraints,
        )
        llm_response_stream = self.llm.query_one_stream_generator(prompt)
        return prompt, llm_response_stream

    def process_LLM_response(self, parsed_response:dict) -> Tuple[ActionType, Dict, Message]:
        """ process the LLM response, single round
        return: (action_type, msgs)
        """
        action_metas = {}
        
        # -> ActionType
        assert "action_type" in parsed_response, f"parsed_response: {parsed_response}"
        try:
            action_type = ActionType[parsed_response["action_type"]]
        except KeyError:
            raise ValueError(f"Unknown action_type: {parsed_response['action_type']}")
        # -> action_metas
        action_name, action_parameters, response = parsed_response.get("action_name", "DEFTAULT_ACTION"), parsed_response.get("action_parameters", "DEFAULT_PARAS"), parsed_response.get("response", "DEFAULT_RESPONSE")
        action_metas.update(action_name=action_name, action_parameters=action_parameters, response=response)
        
        # -> msg
        if action_type == ActionType.API:
            msg = Message(Role.BOT, f"<Call API> {action_name}({action_parameters})")        # bot_callapi_template
        else:
            msg = Message(Role.BOT, response)
        return action_type, action_metas, msg
