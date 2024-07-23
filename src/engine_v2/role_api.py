""" 
process API calls
- `V01APIHandler`: call the API directly
- `ManualAPIHandler`: Fake the API response by manual input

@240723 V01APIHandler 通过 LLM 来进行API格式转换
"""

import requests, json, traceback
from typing import List, Dict, Optional

from .datamodel import BaseRole, Config, Role, Message, Conversation, PDL, ActionType
from .common import prompt_user_input, FN_api_infos, init_client, LLM_CFG
from easonsi.llm.openai_client import OpenAIClient, Formater
from utils.jinja_templates import jinja_render

def handle_exceptions(func):
    """ 异常捕获, 返回错误信息 -> for LLM understaning!
    ref: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # print(e)
            print(traceback.format_exc())
            return {'status': 'error', 'message': str(e)}
    return wrapper


class ManualAPIHandler(BaseRole):
    def process(self, conversation:Conversation, paras:Dict, **kwargs):
        api_name, api_params = paras["action_name"], paras["action_parameters"]
        res = prompt_user_input(f"  <manual> please fake the response of the API call {api_name}({api_params}): ")
        msg = Message(Role.SYSTEM, res)
        return ActionType.API_RESPONSE, None, msg


class LLMSimulatedAPIHandler(BaseRole):
    llm: OpenAIClient
    
    def __init__(self, cfg:Config) -> None:
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.api_model_name])
    
    @handle_exceptions
    def process_llm_response(self, llm_response:str) -> str:
        parsed_response = Formater.parse_llm_output_json(llm_response)
        api_results = parsed_response["response"]
        # if parsed_response["error_code"] != 0:
        #     return f"API Error: {parsed_response['error_code']}, {parsed_response['error_message']}"
        # else:
        #     return parsed_response["response"]
        return api_results

    def process(self, conversation:Conversation, paras:Dict, **kwargs):
        # Just follow the return structure of Role.process
        action_metas = {}
        # TODO: optimize the prompt
        api_name, api_params_list = paras["action_name"], paras["action_parameters"]
        prompt = jinja_render(
            "api_llm_v1.jinja",
            conversation=conversation.to_str(),
            api_name=api_name,
            api_params=str(api_params_list)
        )
        llm_response = self.llm.query_one(prompt)
        action_metas.update(prompt=prompt, llm_response=llm_response)       # for debug
        
        msg = Message(Role.SYSTEM, self.process_llm_response(llm_response))
        return ActionType.API_RESPONSE, action_metas, msg


class V01APIHandler(BaseRole):
    api_infos: Dict[str, Dict] = {}
    
    def __init__(self, fn_api_infos=FN_api_infos):
        """ 
        args:
            fn_api_infos: str, path of the API infos
        """
        self.fn_api_infos = fn_api_infos
        self.api_infos = self.load_api_infos()

    def load_api_infos(self):
        with open(self.fn_api_infos, 'r') as f:
            api_infos = json.load(f)
        api_infos_map = {}
        """ 
        {
            "name": "API-科室校验",
            "description": "校验科室信息",
        }
        """
        for api in api_infos:
            api_infos_map[api["name"]] = api
            api_infos_map[api["name"].rstrip('API-')] = api
            api_infos_map[api["description"]] = api
        return api_infos_map
    
    @staticmethod
    def _call_api(api_info, api_params):
        assert "Method" in api_info and "URL" in api_info, f"API should provide Method and URL!"
        if api_info["Method"] == "POST":
            response = requests.post(api_info["URL"], data=json.dumps(api_params))
        elif api_info["Method"] == "GET":
            response = requests.get(api_info["URL"], params=api_params)
        else:
            raise ValueError(f"Method {api_info['Method']} not supported.")
        response = json.loads(response.content)
        return response

    @handle_exceptions
    def process_api(self, paras:Dict):
        """ 返回统一的 API 调用结果
        return: {'status': 'success', 'response': '{"医院存在类型": "0"}'}
        ref: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
        """
        # 1] call the api
        api_name, api_params_list = paras["action_name"], paras["action_parameters"]
        assert api_name in self.api_infos, f"API `{api_name}` not found!"
        api_info = self.api_infos[api_name]
        
        expected_parameters = list(api_info["parameters"]["properties"].keys())
        assert len(api_params_list) == len(expected_parameters), f"API {api_name} expects parameters {expected_parameters}!"
        api_params_dict = dict(zip(expected_parameters, api_params_list))
        response = self._call_api(api_info, api_params_dict)
        
        # 2] parse the response
        expected_response_properties = api_info["response"]["properties"]
        ret = {}
        for param in expected_response_properties:
            if param in response:
                ret[expected_response_properties[param]['name']] = response[param]
        if len(ret) == 0:    # 如果返回结果中没有有效的参数，则返回原始response
            ret = response
        return {"status": "success", "response": json.dumps(ret, ensure_ascii=False)}

    def process(self, conversation:Conversation, paras:Dict, **kwargs):
        # Just follow the return structure of Role.process
        msg = Message(Role.SYSTEM, self.process_api(paras))
        return ActionType.API_RESPONSE, None, msg