""" 
@240718 从 engine_v1.bots 进行修改修改
"""

from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from engine_v1.datamodel import BaseBot, Logger, BaseLogger, BaseAPIHandler, Role, Message, Conversation, PDL, ActionType, ConversationInfos
from utils.jinja_templates import jinja_render

class PDL_UIBot(BaseBot):
    """ 在的 engine_v1 的版本上分拆 process 函数, 以适应 streamlit 交互 """
    logger: Logger = BaseLogger()
    api_handler: BaseAPIHandler = None
    client: OpenAIClient = None
    # configs
    template_fn: str = None
    pdl: PDL = PDL()
    
    def __init__(self, client: OpenAIClient, api_handler: BaseAPIHandler, logger:Logger, template_fn:str="query_PDL.jinja"):
        self.api_handler = api_handler
        self.client = client
        self.logger = logger
        # configs
        self.template_fn = template_fn

    def _load_pdl(self,fn:str):
        self.pdl.load_from_file(fn)

    def process_stream(self, conversation: Conversation, conversation_infos: ConversationInfos = None):
        if conversation_infos:
            s_current_state = f"Previous action type: {conversation_infos.previous_action_type}. The number of user queries: {conversation_infos.num_user_query}."
        prompt = jinja_render(
            self.template_fn,       # "query_PDL.jinja"
            conversation=conversation.to_str(), 
            PDL=self.pdl.to_str(),
            current_state=s_current_state if conversation_infos else None
        )
        llm_response_stream = self.client.query_one_stream_generator(prompt)
        return prompt, llm_response_stream

    def process_LLM_response(self, conversation:Conversation, parsed_response:dict) -> Tuple[Tuple, List[Message]]:
        """ process the LLM response, single round
        return: (action_type, msgs)
        """
        s_action_type = parsed_response["action_type"]
        if s_action_type == "REQUEST":
            action_type = ActionType.REQUEST
        elif s_action_type == "ANSWER":
            action_type = ActionType.ANSWER
        elif s_action_type == "API":
            action_type = ActionType.API
        else:
            raise ValueError(f"Unknown action_type: {s_action_type}")
        
        action_name, action_paras, response = parsed_response.get("action_name", "DEFTAULT_ACTION"), parsed_response.get("action_parameters", "DEFAULT_PARAS"), parsed_response.get("response", "DEFAULT_RESPONSE")
        if action_type == ActionType.API:
            conversation.add_message(Message(Role.BOT, f"<Call API> {action_name}({action_paras})"))
            API_resonse = self.api_handler.process_query(conversation, action_name, action_paras)
            conversation.add_message(Message(Role.SYSTEM, f"<API response> {API_resonse}"))
        else:
            conversation.add_message(Message(Role.BOT, response))
        return action_type
