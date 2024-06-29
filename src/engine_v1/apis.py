""" 
处理 API 请求

`ManualAPIhandler`: Fake the API response by manual input
"""

from typing import List, Dict, Optional


class BaseAPIHandler:
    def process_query(self, s_conversation:str, api_name: str, api_params: Dict) -> str:
        raise NotImplementedError

class ManualAPIhandler(BaseAPIHandler):
    def process_query(self, s_conversation: str, api_name: str, api_params: Dict) -> str:
        # return super().process_query(s_conversation, api_name, api_params)
        res = input(f"<debug> please fake the response of the API call {api_name}({api_params}): ")
        return res