""" 
process API calls
- `V01APIHandler`: call the API directly
- `ManualAPIHandler`: Fake the API response by manual input

@240723 V01APIHandler 通过 LLM 来进行API格式转换
@240802 add EntityLinker
"""

import requests, json, traceback
from typing import List, Dict, Optional

from .datamodel import BaseRole, Config, Role, Message, Conversation, PDL, ActionType
from .common import prompt_user_input, _DIRECTORY_MANAGER, init_client, LLM_CFG, DEBUG
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



class EntityLinker:
    """ abstract of entity linking """
    cfg: Config = None
    llm: OpenAIClient
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.api_model_name])
        if DEBUG: print(f">> [api] init EL model {cfg.api_model_name} with {json.dumps(LLM_CFG[cfg.api_model_name], ensure_ascii=False)}")

    def entity_linking(self, query:str, eneity_list: List[str]) -> Dict:
        """ Given a list of candidate entities, use llm to determine which one is most similor to the input
        return : 
        """
        meta = {}
        
        # if DEBUG: print(f">> runing EL for {query} with {json.dumps(eneity_list, ensure_ascii=False)}")
        res = {
            "is_matched": True, 
            "matched_entity": None
        }
        prompt = jinja_render("entity_linking.jinja", query=query, eneity_list=eneity_list)
        # if DEBUG: print(f"  model: {self.llm}\n  prompt: {json.dumps(prompt, ensure_ascii=False)}")
        llm_response = self.llm.query_one(prompt)
        # if DEBUG: print(f"  llm_response: {json.dumps(llm_response, ensure_ascii=False)}")
        meta.update(prompt=prompt, llm_response=llm_response)
        
        # todo: error handling
        parsed_response = Formater.parse_llm_output_json(llm_response)
        if parsed_response["is_matched"]: res["matched_entity"] = parsed_response["matched_entity"]
        else: res["is_matched"] = False
        return res, meta



class BaseAPIHandler(BaseRole):
    """ 
    API structure: (see apis_v0/apis.json)
  {
    "name": "API-校验挂号医院",
    "description": "校验挂号医院",
    "parameters": {
      "type": "object",
      "properties": {
        "hos_name": {
          "type": "string",
          "name": "医院名称",
          "description": "医院名称",
          "entity_list": ["北京301医院", "北京安贞医院", "北京朝阳医院", "北京大学第一医院", "北京大学人民医院", "北京儿童医院", "北京积水潭医院", "北京世纪坛医院", "北京天坛医院", "北京协和医学院附属肿瘤医院", "北京协和医院", "北京宣武医院", "北京友谊医院", "北京中日友好医院", "北京中医药大学东方医院", "北京中医药大学东直门医院"]
        }
      },
      "required": [
        "hos_name"
      ]
    },
    "response": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "name": "医院存在类型",
          "description": "医院存在类型"
        }
      }
    },
    "URL": "http://11.141.203.151:8089/jiaoyanyiyuan",
    "Method": "GET"
  },
    """
    cfg: Config = None              # cfg.workflow_name
    names: List[str] = []                   # for convert name2role
    fn_api_infos: str = _DIRECTORY_MANAGER.FN_api_infos
    api_infos_map: Dict[str, Dict] = {}
    entity_linker: EntityLinker = None
    conversation: Conversation = None

    def __init__(self, cfg:Config, *args, **kwargs) -> None:
        self.cfg = cfg
        if cfg.fn_api_infos: self.fn_api_infos = cfg.fn_api_infos
        self.api_infos_map = self.load_api_infos(self.fn_api_infos)
        if cfg.api_entity_linking: self.entity_linker = EntityLinker(cfg=cfg)

    def load_api_infos(self, fn_api_infos: str):
        if DEBUG: print(f">> Loading API infos from {fn_api_infos}")
        with open(fn_api_infos, 'r') as f:
            api_infos = json.load(f)
        api_infos_map = {}
        for api in api_infos:
            # only select apis from current workflow
            if api["from"] != self.cfg.workflow_name: continue
            api_infos_map[api["name"]] = api
        return api_infos_map
    
    @handle_exceptions
    def match_and_check_api(self, paras:Dict, action_metas:Dict, **kwargs):
        """ Maybe ERROR!
        args:
            action_metas: hock
        return:
            api_info: matched API 
            api_params_dict: {"param_name": "param_value"}
            
        """
        api_name, input_params = paras["action_name"], paras["action_parameters"]
        assert api_name in self.api_infos_map, f"API `{api_name}` not found!"
        api_info = self.api_infos_map[api_name]
        
        api_params = api_info["parameters"]["properties"]
        expected_param_names = list(api_params.keys())
        if isinstance(input_params, list):
            assert len(input_params) == len(expected_param_names), f"API {api_name} expects {len(expected_param_names)} parameters {expected_param_names}, but got {len(input_params)} input parameters!"
        if isinstance(input_params, dict):
            assert all(k in expected_param_names for k in input_params.keys()), f"API {api_name} expects parameters {expected_param_names}!"
            input_params = [input_params[k] for k in expected_param_names]
        api_params_dict = dict(zip(expected_param_names, input_params))
    
        # check the parameters! @240802
        if self.cfg.api_entity_linking:
            if DEBUG: 
                print(f">> entity linking for `{api_name}` ... with input {json.dumps(api_params_dict, ensure_ascii=False)}")
                # print(f"  {json.dumps(api_params, ensure_ascii=False)}\n  {expected_param_names} with {input_params}")
            for param_name, param_input in zip(expected_param_names, input_params):
                param_info = api_params[param_name]
                if "entity_list" in param_info and param_info["entity_list"]:
                    res, _meta = self.entity_linker.entity_linking(param_input, param_info["entity_list"])
                    action_metas["entity_linking_log"].append(_meta)
                    if res["is_matched"]: 
                        if DEBUG: print(f"  {param_input} -> {res['matched_entity']}")
                        api_params_dict[param_name] = res["matched_entity"]
                    else: 
                        if DEBUG: print(f"  {param_input} <-x-> {res['matched_entity']}")
                        # raise ValueError(f"Failed to link entity {param_input} to {param_info['entity_list']}")
            # if DEBUG: print(f">> api_params_dict: {api_params_dict}")
        return api_info, api_params_dict

    def update_conversation(self, api_info:Dict, api_params_dict:Dict):
        # update the matched params to conversation
        matched_api_params = [api_params_dict[k] for k in list(api_info["parameters"]["properties"].keys())]
        self.conversation.add_message(Message(Role.SYSTEM, f"Entity linked! Actually called API: {api_info['name']}({matched_api_params})"))
    
    def update_conversation_back(self, m:str):
        tmp_msg = self.conversation.msgs.pop()
        return Message(Role.SYSTEM, f"{tmp_msg.content}\n{m}")

class ManualAPIHandler(BaseAPIHandler):
    names = ["manual", "ManualAPIHandler"]
    def process(self, conversation:Conversation, paras:Dict, **kwargs):
        api_name, api_params = paras["action_name"], paras["action_parameters"]
        res = prompt_user_input(f"  <manual> please fake the response of the API call {api_name}({api_params}): ")
        msg = Message(Role.SYSTEM, res)
        return ActionType.API_RESPONSE, None, msg


class LLMSimulatedAPIHandler(BaseAPIHandler):
    llm: OpenAIClient
    names = ["llm", "LLMSimulatedAPIHandler"]
    
    def __init__(self, cfg:Config) -> None:
        super().__init__(cfg=cfg)
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.api_model_name])
    
    @handle_exceptions
    def process_llm_response(self, llm_response:str) -> str:
        parsed_response = Formater.parse_llm_output_json(llm_response)
        # api_results = parsed_response["response"]
        return parsed_response

    def process(self, conversation:Conversation, paras:Dict, **kwargs):
        self.conversation = conversation
        action_metas = {
            "query": {
                "action_name": paras["action_name"],
                "action_parameters": paras["action_parameters"]
            },
            "matched": {
                "action_name": "",
                "action_parameters_dict": {}
            },
            "entity_linking_log": []
        }       # for debug
        # if self.cfg.api_model_entity_linking:
        res = self.match_and_check_api(paras, action_metas)   # match the standard API
        if isinstance(res, dict):
            msg = Message(Role.SYSTEM, json.dumps(res, ensure_ascii=False))
        else:
            api_info, api_params_dict = res
            api_name = api_info["name"]
            if self.cfg.api_entity_linking:
                # NOTE: update the matched params to conversation
                self.update_conversation(api_info, api_params_dict)
            prompt = jinja_render(
                "api_llm.jinja",
                API=self.api_infos_map[api_name],       # get api info!
                conversation=conversation.to_str(),
                # api_name=api_name if not self.cfg.api_model_entity_linking else api_info["name"],
                # api_params=str(api_params_list if not self.cfg.api_model_entity_linking else api_params_dict)   # TODO: test dict/list
                api_name=api_name,
                api_params=str(api_params_dict)
            )
            llm_response = self.llm.query_one(prompt)
            action_metas.update(prompt=prompt, llm_response=llm_response)       # for debug
            res = self.process_llm_response(llm_response)
            res = f"<API response> {res}"
            if self.cfg.api_entity_linking:
                msg = self.update_conversation_back(res)
            else:
                msg = Message(Role.SYSTEM, res)
        return ActionType.API_RESPONSE, action_metas, msg



class V01APIHandler(BaseAPIHandler):
    entity_linker: EntityLinker = None
    names = ["v01", "V01APIHandler"]
    
    def __init__(self, cfg:Config):
        """ 
        args:
            fn_api_infos: str, path of the API infos
        """
        super().__init__(cfg=cfg)
        if cfg.api_entity_linking: self.entity_linker = EntityLinker(cfg=cfg)

    @staticmethod
    def _call_api(api_info, api_params_dict):
        assert "Method" in api_info and "URL" in api_info, f"API should provide Method and URL!"
        if api_info["Method"] == "POST":
            response = requests.post(api_info["URL"], data=json.dumps(api_params_dict))
        elif api_info["Method"] == "GET":
            response = requests.get(api_info["URL"], params=api_params_dict)
        else:
            raise ValueError(f"Method {api_info['Method']} not supported.")
        response = json.loads(response.content)
        return response

    @handle_exceptions
    def process_api(self, api_info, api_params_dict, action_metas:Dict, **kwargs):
        """ 返回统一的 API 调用结果
        return: {'status': 'success', 'response': '{"医院存在类型": "0"}'}
        ref: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
        """

        # 1] call the api
        # NOTE: update the matched params to conversation
        if self.cfg.api_entity_linking:
            self.update_conversation(api_info, api_params_dict)
        action_metas["matched"]["action_parameters_dict"] = api_params_dict
        action_metas["matched"]["action_name"] = api_info["name"]
        response = self._call_api(api_info, api_params_dict)
        
        # 2] parse the response
        expected_response_properties = api_info["response"]["properties"]
        ret = {}
        for param in expected_response_properties:
            if param in response:
                ret[expected_response_properties[param]['name']] = response[param]
        if len(ret) == 0:    # 如果返回结果中没有有效的参数，则返回原始response
            ret = response
        return json.dumps(
            {"status": "success", "response": ret}, 
            ensure_ascii=False
        )

    def process(self, conversation:Conversation, paras:Dict, **kwargs):
        """ 
        args:
            conversation: 
            paras: {action_name:str, action_parameters:list}
        """
        self.conversation = conversation
        action_metas = {
            "query": {
                "action_name": paras["action_name"],
                "action_parameters": paras["action_parameters"]
            },
            "matched": {
                "action_name": "",
                "action_parameters_dict": {}
            },
            "entity_linking_log": []
        }       # for debug
        res = self.match_and_check_api(paras, action_metas)   # match the standard API
        if isinstance(res, dict):
            msg = Message(Role.SYSTEM, json.dumps(res, ensure_ascii=False))
        else:
            api_info, api_params_dict = res
            # TODO: log the entity linking
            res = self.process_api(api_info, api_params_dict, action_metas)
            res = f"<API response> {res}"
            if self.cfg.api_entity_linking:
                msg = self.update_conversation_back(res)
            else:
                msg = Message(Role.SYSTEM, res)
        return ActionType.API_RESPONSE, action_metas, msg



API_NAME2CLASS:Dict[str, BaseAPIHandler] = {}
# for c in [V01APIHandler, ManualAPIHandler, LLMSimulatedAPIHandler]:
for cls in BaseAPIHandler.__subclasses__():
    for name in cls.names:
        API_NAME2CLASS[name] = cls