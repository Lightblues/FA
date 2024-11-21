""" 
from [branch agent-pdl] src/engine/role_api.py
- [x] 统一API的格式定义  -- 修复现在版本的 API! 
- [ ] 增加 entity linker
"""

from typing import Dict, Tuple
import requests, json, traceback
from ..base import BaseAPIHandler
from ...data import APIOutput, BotOutput, Role, Message, Config

def handle_exceptions(func):
    """ 异常捕获, 返回错误信息 -> for LLM understaning!
    ref: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(traceback.format_exc())
            return {'status': 'error', 'message': str(e)}
    return wrapper


class RequestAPIHandler(BaseAPIHandler):
    # entity_linker: EntityLinker = None
    names = ["v01", "request", "RequestAPIHandler"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        # TODO: entity linker
        # if cfg.api_entity_linking: self.entity_linker = EntityLinker(cfg=cfg)
        self._build_api_infos_map()
        
    def _build_api_infos_map(self):
        self.api_infos_map = {}
        for api in self.api_infos:
            self.api_infos_map[api["name"]] = api
            self.api_infos_map[api["description"]] = api
            
    def refresh_config(self, cfg: Config):
        """For UI! """
        self.cfg = cfg
        self.api_infos = self.workflow.toolbox
        self._build_api_infos_map()

    @staticmethod
    def _call_api(api_info: Dict, api_params_dict: Dict):
        # assert "Method" in api_info and "URL" in api_info, f"API should provide Method and URL!"
        if api_info["method"] == "POST":
            # if DEBUG: print(f">> calling [{api_info['name']}] -- {api_info['URL']} with params {api_params_dict}")
            response = requests.post(api_info["url"], data=json.dumps(api_params_dict))
        elif api_info["method"] == "GET":
            response = requests.get(api_info["url"], params=api_params_dict)
        else:
            raise ValueError(f"Method {api_info['Method']} not supported.")
        response = json.loads(response.content)
        return response

    # @handle_exceptions
    def _process_api(self, api_info, api_params_dict, apicalling_info:BotOutput, **kwargs):
        """ 返回统一的 API 调用结果
        return: {'status': 'success', 'response': '{"医院存在类型": "0"}'}
        ref: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
        """
        # 1] call the api
        # NOTE: update the matched params to conversation
        # if self.cfg.api_entity_linking:
        #     self.update_conversation(api_info, api_params_dict)
        # action_metas.apicalling_info_matched = APICalling_Info(name=api_info["name"], kwargs=api_params_dict)
        response = self._call_api(api_info, api_params_dict)
        
        # # 2] parse the response
        # expected_response_properties = api_info["response"]["properties"]
        # ret = {}
        # for param in expected_response_properties:
        #     if param in response:
        #         ret[expected_response_properties[param]['name']] = response[param]
        # if len(ret) == 0:    # 如果返回结果中没有有效的参数，则返回原始response
        #     ret = response
        # return json.dumps(
        #     {"status": "success", "response": ret}, 
        #     ensure_ascii=False
        # )
        # return json.dumps(response, ensure_ascii=False)
        return APIOutput(
            name=apicalling_info.action,
            request=apicalling_info.action_input,
            response_data=json.dumps(response, ensure_ascii=False),
            response_status_code=200, # int(result[APIOutput.response_status_str_react]),
        )

    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        # if DEBUG: print(f">> process API with apicalling_info {apicalling_info}")
        #     res = f"<API response> {res}"
        #     if self.cfg.api_entity_linking:
        #         msg = self.update_conversation_back(res)
        #     else:
        #         msg = Message(Role.SYSTEM, res)
        # return ActionType.API_RESPONSE, action_metas, msg
        
        # 1. match the api
        try:
            api_info, api_params_dict = self._match_and_check_api(apicalling_info)   # match the standard API
        except Exception as e:
            msg = Message(
                Role.SYSTEM, f"<API response> {str(e)}", 
                conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
            )
            self.conv.add_message(msg)
            return None
        # 2. call the api
        prediction = self._process_api(api_info, api_params_dict, apicalling_info)

        if prediction.response_status_code==200:
            msg_content = f"<API response> {prediction.response_data}"
        else:
            msg_content = f"<API response> {prediction.response_status_code} {prediction.response_data}"
        msg = Message(
            Role.SYSTEM, msg_content, # prompt=prompt, llm_response=llm_response, 
            conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
        )
        self.conv.add_message(msg)
        return prediction

    # @handle_exceptions
    def _match_and_check_api(self, apicalling_info: BotOutput, **kwargs) -> Tuple[str, Dict]:
        """ Maybe ERROR!
        args:
            action_metas: hock
        return:
            api_info: matched API 
            api_params_dict: {"param_name": "param_value"}
        """
        api_name, api_arguments = apicalling_info.action, apicalling_info.action_input
        # 1. check the API name
        assert api_name in self.api_infos_map, f"API `{api_name}` not found!"
        api_info = self.api_infos_map[api_name]
        
        # 2. check the parameters all match the API
        assert isinstance(api_arguments, dict), f"API `{api_name}` expects parameters as dict!"
        if not ("parameters" in api_info and isinstance(api_info["parameters"], dict) and "properties" in api_info["parameters"]):
            return api_info, api_arguments
        api_params = api_info["parameters"]["properties"]
        # TODO: the "required"
        assert all(k in api_params for k in api_arguments.keys()), f"API {api_name} expects parameters {api_params.keys()}!"
    
        # # 3. entity linking @240802
        # if self.cfg.api_entity_linking:
        #     if DEBUG: print(f">> entity linking for `{api_name}` ... with input {input_params}")
        #     for param_name, param_input in input_params.items():
        #         param_info = api_params[param_name]
        #         if "entity_list" in param_info and param_info["entity_list"]:
        #             res, _meta = self.entity_linker.entity_linking(param_input, param_info["entity_list"])
        #             action_metas.entity_linking_log.append(_meta)
        #             if res["is_matched"]: 
        #                 if DEBUG: print(f"  {param_input} -> {res['matched_entity']}")
        #                 input_params[param_name] = res["matched_entity"]
        #             else: 
        #                 if DEBUG: print(f"  {param_input} <-x-> {res['matched_entity']}")
        return api_info, api_arguments