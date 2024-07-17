
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from .datamodel import BaseBot, Logger, BaseLogger, BaseAPIHandler, Role, Message, Conversation, PDL, ActionType, ConversationInfos
from .common import LLM_stop
from utils.jinja_templates import jinja_render

class PDLBot(BaseBot):
    logger: Logger = BaseLogger()
    api_handler: BaseAPIHandler = None
    client: OpenAIClient = None
    # configs
    template_fn: str = None
    pdl: PDL = None
    
    def __init__(self, client: OpenAIClient, api_handler: BaseAPIHandler, logger:Logger, template_fn:str="query_PDL.jinja"):
        self.api_handler = api_handler
        self.client = client
        self.logger = logger
        # configs
        self.template_fn = template_fn

    def _load_pdl(self,fn:str):
        self.pdl = PDL()
        self.pdl.load_from_file(fn)
        
    def process(self, conversation: Conversation, conversation_infos: ConversationInfos = None) -> Tuple[ActionType, List[Message]]:
        if conversation_infos:
            s_current_state = f"Previous action type: {conversation_infos.previous_action_type}. The number of user queries: {conversation_infos.num_user_query}."
        prompt = jinja_render(
            self.template_fn,       # "query_PDL.jinja"
            conversation=conversation.to_str(), 
            PDL=self.pdl.to_str(),
            current_state=s_current_state if conversation_infos else None
        )
        llm_response = self.client.query_one_stream(prompt, stop=LLM_stop)
        _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<prompt>>\n{prompt}\n\n<<response>>\n{llm_response}\n"
        self.logger.debug(_debug_msg)
        
        # parse the generated response
        parsed_response = Formater.parse_llm_output_json(llm_response)
        a_type, msgs = self._process_LLM_response(conversation, parsed_response)
        
        conversation += msgs
        return a_type, msgs

    def _process_LLM_response(self, conversation:Conversation, parsed_response:dict) -> Tuple[Tuple, List[Message]]:
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
        
        messages = []
        action_name, action_paras, response = parsed_response.get("action_name", "DEFTAULT_ACTION"), parsed_response.get("action_parameters", "DEFAULT_PARAS"), parsed_response.get("response", "DEFAULT_RESPONSE")
        if action_type == ActionType.API:
            API_resonse = self.api_handler.process_query(conversation, action_name, action_paras)
            messages += (
                Message(Role.BOT, f"<Call API> {action_name}({action_paras})"),
                Message(Role.SYSTEM, f"<API response> {API_resonse}"),
            )

        elif action_type in [ActionType.REQUEST, ActionType.ANSWER]:
            messages.append(
                Message(Role.BOT, response)
            )
        else:
            print(f"[ERROR] Unknown action_type: {parsed_response['action_type']}\n{parsed_response}")
        return action_type, messages
