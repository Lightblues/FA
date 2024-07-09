""" 
处理 API 请求

- `ManualAPIhandler`: Fake the API response by manual input
- `LLMAPIHandler`: LLM fake the API response
- `VanillaCallingAPIHandler`: Call the API directly
"""
import requests
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater
from .prompts import get_llm_API_prompt
from .datamodel import Conversation
from .common import LLM_stop, API_base_rul, API_infos

APIs = {}

def register_api(api_info):
    global APIs
    APIs[api_info["name"]] = api_info
    APIs[api_info["endpoint"]] = api_info


def call_py_name_and_paras(api_name: str, api_paras: List[str]):
    base_url = API_base_rul
    
    api_name = api_name.strip().lstrip("API-")
    if api_name in APIs:
        api_info = APIs[api_name]
        endpoint = api_info["endpoint"]
        api_type = api_info["type"]
        request_data = dict(zip(api_info["request"], api_paras))
        if api_type == "POST":
            response = requests.post(base_url + endpoint, json=request_data)
        elif api_type == "GET":
            response = requests.get(base_url + endpoint, params=request_data)
        else:
            return {"error": f"API {api_name} type {api_type} not supported", "status_code": 404}
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text, "status_code": response.status_code}
    else:
        return {"error": f"API {api_name} not found", "status_code": 404}


class BaseAPIHandler:
    def process_query(self, conversation:Conversation, api_name: str, api_params: Dict) -> str:
        raise NotImplementedError

class ManualAPIHandler(BaseAPIHandler):
    def process_query(self, conversation: str, api_name: str, api_params: Dict) -> str:
        # return super().process_query(s_conversation, api_name, api_params)
        res = input(f"<debug> please fake the response of the API call {api_name}({api_params}): ")
        return res

class LLMAPIHandler(BaseAPIHandler):
    def __init__(self, client: OpenAIClient):
        self.client = client
    def process_query(self, conversation: Conversation, api_name: str, api_params: Dict) -> str:
        if isinstance(conversation, Conversation):
            conversation = conversation.to_str()
        prompt = get_llm_API_prompt(conversation, api_name, str(api_params))
        llm_response = self.client.query_one_stream(prompt, stop=LLM_stop)
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

class VanillaCallingAPIHandler(BaseAPIHandler):
    def __init__(self) -> None:
        for api_info in API_infos:
            register_api(api_info)
    def process_query(self, conversation: Conversation, api_name: str, api_params: Dict) -> str:
        return call_py_name_and_paras(api_name, api_params)
