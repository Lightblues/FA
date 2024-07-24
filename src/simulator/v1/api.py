""" 
@240716: ConversationSimulatorAPIHandler
"""
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater

from engine_v1.apis import BaseAPIHandler
from engine_v1.datamodel import Conversation, Logger
from engine_v1.common import LLM_stop
from utils.jinja_templates import jinja_render

class ConversationSimulatorAPIHandler(BaseAPIHandler):
    """ 给定ref_conversation的情况下模拟生成API回复 """
    ref_conversation: Conversation
    client: OpenAIClient
    logger: Logger = None
    
    def __init__(self, ref_conversation:Conversation, client:OpenAIClient, logger:Logger) -> None:
        self.ref_conversation = ref_conversation
        self.client = client
        self.logger = logger
    
    def process_query(self, conversation: Conversation, api_name: str, api_params: Dict) -> str:
        prompt = jinja_render(
            "api_llm_simulator.jinja",
            ref_conversation=self.ref_conversation.to_str(),
            new_conversation=conversation.to_str(),
            api_name=api_name, api_params=api_params,
        )
        llm_response = self.client.query_one_stream(prompt, stop=LLM_stop)
        _debug_msg = f"{'[API]'.center(50, '=')}\n<<prompt>>\n{prompt}\n\n<<response>>\n{llm_response}\n"
        self.logger.debug(_debug_msg)
        try:
            parsed_response = Formater.parse_llm_output_json(llm_response)
            if parsed_response["error_code"] != 0:
                return f"API Error: {parsed_response['error_code']}, {parsed_response['error_message']}"
            else:
                return parsed_response["response"]
        except Exception as e:
            return f"Unknown API Error: {e}"