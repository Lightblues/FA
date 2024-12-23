"""
@241212
- [x] Unified API format! - OpenAI function calling https://platform.openai.com/docs/guides/function-calling
- [x] add entity linker
@241221
- [x] #feat update tool (dict -> ExtToolSpec)

- [ ] tackle entity linking??
"""

import copy
import json
import traceback
from typing import Dict, List, Tuple

import requests
from loguru import logger
from pydantic import Field

from data import APIOutput, BotOutput, Role
from data.pdl.tool import ExtToolSpec
from ..entity_linker import EntityLinker
from .base_tool import BaseTool
from .tool_mock_mixin import ToolMockMixin


def handle_exceptions(func):
    """异常捕获, 返回错误信息 -> for LLM understaning!
    ref: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(traceback.format_exc())
            return {"status": "error", "message": str(e)}

    return wrapper


class RequestTool(BaseTool, ToolMockMixin):
    """
    Used config:
        api_entity_linking
        (EntityLinker) api_entity_linking_llm, api_entity_linking_template

    Usage:
        request_tool = RequestTool(cfg=cfg, conv=conv, workflow=workflow)
        bot_output = BotOutput(thought="...", action="check_hospital_exist", action_input={"hos_name": "test"}, response=None)
        api_output = request_tool.process(bot_output)
        print(api_output)
    """

    names = ["v01", "request", "RequestAPIHandler"]

    api_entity_linking: bool = False
    entity_linker: EntityLinker = None

    tool_map: Dict[str, ExtToolSpec] = Field(default_factory=dict)

    def _post_init(self) -> None:
        self.api_entity_linking = self.cfg.api_entity_linking

        if self.api_entity_linking:
            self.entity_linker = EntityLinker(cfg=self.cfg, conv=self.context.conv)
        self._build_api_infos_map()

    def _build_api_infos_map(self):
        self.tool_map = {}
        for api in self.context.data_handler.toolbox:
            self.tool_map[api.name] = api  # also use tool.description as key?
        logger.info(f">>> tool names: {list(self.tool_map.keys())}")

    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        """main function to process the request (bot_output)

        Args:
            apicalling_info (BotOutput): the calling info (with ``.action``, ``.action_input``)

        Returns:
            APIOutput: api output, with ``.response_status_cod``e and ``.response_data``

        Usage::

            request_tool = RequestTool(cfg=cfg, conv=conv, workflow=pdl)
            bot_output = BotOutput(thought="...", action="check_hospital_exist", action_input={"hos_name": "test"}, response=None)
            api_output = request_tool.process(bot_output)
            print(api_output)
        """
        logger.info(f"process api calling info: {apicalling_info}")
        # 1. match the api
        try:
            api_spec, api_params_dict = self._match_and_check_api(apicalling_info)  # match the standard API
        except Exception as e:
            self.context.conv.add_message(f"<API response> {str(e)}", role=Role.SYSTEM)
            return APIOutput(
                name=apicalling_info.action,
                request=apicalling_info.action_input,
                response_status_code=500,
                response_data=str(e),
            )
        # 2. call the api
        prediction = self._process_api(api_spec, api_params_dict, apicalling_info)
        # 3. add message
        if prediction.response_status_code == 200:
            msg_content = f"<API response> {prediction.response_data}"
        else:
            msg_content = f"<API response> {prediction.response_status_code} {prediction.response_data}"
        self.context.conv.add_message(msg_content, role=Role.SYSTEM)
        return prediction

    # @handle_exceptions
    def _match_and_check_api(self, apicalling_info: BotOutput, **kwargs) -> Tuple[ExtToolSpec, Dict]:
        """Maybe ERROR!
        args:
            action_metas: hock
        return:
            api_info: matched API
            api_params_dict: {"param_name": "param_value"}
        """
        api_name, api_arguments = apicalling_info.action, apicalling_info.action_input
        # 1. check the API name
        if "." in api_name:
            logger.warning(f"API name contains dot! {api_name} -> {api_name.split('.')[-1]}")
            api_name = api_name.split(".")[-1]
        assert api_name in self.tool_map, f"API `{api_name}` not found!"
        api_spec = self.tool_map[api_name]

        # 2. check the parameters all match the API
        assert isinstance(api_arguments, dict), f"API `{api_name}` expects parameters as dict! Input: {api_arguments}"
        _params_set = set(api_spec.parameters.properties.keys())
        # TODO: the "required"
        assert all(k in _params_set for k in api_arguments.keys()), f"API {api_name} expects parameters {_params_set}!"

        # 3. entity linking @240802
        if self.api_entity_linking:
            # if DEBUG: print(f">> entity linking for `{api_name}` ... with input {input_params}")
            _api_arguments = copy.deepcopy(api_arguments)
            for k, v in api_arguments.items():
                param_info = api_spec.parameters.properties[k]
                if hasattr(param_info, "enum") and param_info.enum:
                    res, _meta = self.entity_linker.entity_linking(v, param_info.enum)
                    if res["is_matched"]:
                        api_arguments[k] = res["matched_entity"]
            # info the entity linking result
            if _api_arguments != api_arguments:
                self.context.conv.add_message(
                    f"entity linked from {json.dumps(_api_arguments, ensure_ascii=False)} to {json.dumps(api_arguments, ensure_ascii=False)}",
                    role=Role.SYSTEM,
                )
            logger.info(f"entity linked from {json.dumps(_api_arguments, ensure_ascii=False)} to {json.dumps(api_arguments, ensure_ascii=False)}")
        return api_spec, api_arguments

    # @handle_exceptions
    def _process_api(
        self,
        api_info: ExtToolSpec,
        api_params_dict: Dict,
        apicalling_info: BotOutput,
        **kwargs,
    ):
        """返回统一的 API 调用结果
        return: {'status': 'success', 'response': '{"医院存在类型": "0"}'}
        ref: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/utils/tool_executor.py
        """
        # 1] call the api
        # action_metas.apicalling_info_matched = APICalling_Info(name=api_info["name"], kwargs=api_params_dict)
        response = self._call_api(api_info, api_params_dict)

        # 2] parse the response? skip now
        return APIOutput(
            name=apicalling_info.action,
            request=apicalling_info.action_input,
            response_data=json.dumps(response, ensure_ascii=False),
            response_status_code=200,  # TODO:
        )

    def _call_api(self, api_spec: ExtToolSpec, api_params_dict: Dict):
        # assert "Method" in api_info and "URL" in api_info, f"API should provide Method and URL!"
        if api_spec.extra_infos:
            extra_infos = api_spec.extra_infos
            print(f"> Mocking result of {extra_infos}...")
            if extra_infos.get("type") == "llm":
                return self.mock_llm(extra_infos.get("prompt"), api_params_dict)
            elif api_spec.extra_infos.get("type") == "code_executor":
                return self.mock_code_executor(extra_infos.get("code"), api_params_dict)
            else:
                raise ValueError(f"Mocking result of {api_spec.extra_infos} not supported!")
        try:
            if api_spec.method == "POST":
                # if DEBUG: print(f">> calling [{api_info['name']}] -- {api_info['URL']} with params {api_params_dict}")
                response = requests.post(api_spec.url, data=json.dumps(api_params_dict))
            elif api_spec.method == "GET":
                response = requests.get(api_spec.url, params=api_params_dict)
            else:
                raise ValueError(f"Method {api_spec.method} not supported.")
            # check the status code
            response.raise_for_status()
            try:
                return response.json()  # instead of json.loads(response.content)
            except json.JSONDecodeError:
                # return the raw response when failed to decode!
                return {"raw_response": response.text}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
