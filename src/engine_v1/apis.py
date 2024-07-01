""" 
处理 API 请求

`ManualAPIhandler`: Fake the API response by manual input
"""

from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater
from .prompts import get_llm_API_prompt
from .datamodel import Conversation

class BaseAPIHandler:
    def process_query(self, s_conversation:str, api_name: str, api_params: Dict) -> str:
        raise NotImplementedError

class ManualAPIHandler(BaseAPIHandler):
    def process_query(self, s_conversation: str, api_name: str, api_params: Dict) -> str:
        # return super().process_query(s_conversation, api_name, api_params)
        res = input(f"<debug> please fake the response of the API call {api_name}({api_params}): ")
        return res

class LLMAPIHandler(BaseAPIHandler):
    def __init__(self, client: OpenAIClient):
        self.client = client
    def process_query(self, s_conversation: Conversation, api_name: str, api_params: Dict) -> str:
        if isinstance(s_conversation, Conversation):
            s_conversation = s_conversation.to_str()
        prompt = get_llm_API_prompt(s_conversation, api_name, str(api_params))
        llm_response = self.client.query_one_stream(prompt)
        errcode, parsed_response = Formater.parse_llm_output_json(llm_response)
        # if errcode:
        #     return "Unknown error!!!"
        # else:
        try:
            if parsed_response["error_code"] != 0:
                return f"API Error: {parsed_response['error_code']}, {parsed_response['error_message']}"
            else:
                return parsed_response["response"]
        except Exception as e:
            return f"Unknown API Error: {e}"