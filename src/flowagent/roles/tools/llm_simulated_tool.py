"""updated @240906
- [ ] generate api response with given history calling infos
- [ ] integrate with FastAPI
"""

import json
import re

from common import LLM_CFG, Formater, OpenAIClient, init_client, jinja_render

from ...data import APIOutput, BotOutput, Role
from ..base import BaseTool


class LLMSimulatedTool(BaseTool):
    """LLMSimulatedTool

    Variables: (self)
        process(): llm, conv
        _gen_prompt(): api_infos, api_template_fn

    Used config:
        api_llm_name
        api_template_fn

    Usage::
        cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
        conv = Conversation()
        pdl = Workflow(cfg)
        tool = LLMSimulatedTool(cfg=cfg, conv=conv, workflow=pdl)

        bot_output = BotOutput(thought="...", action="check_hospital", action_input={"hospital_name": "test"}, response=None)
        api_output: APIOutput = tool.process(bot_output)
    """

    llm: OpenAIClient = None
    api_template_fn: str = "flowagent/api_llm.jinja"
    names = ["llm", "LLMSimulatedAPIHandler"]

    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.llm = init_client(self.cfg.api_llm_name)
        # overwrite the default template
        if self.cfg.api_template_fn is not None:
            self.api_template_fn = self.cfg.api_template_fn

    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        flag, m = self._check_validation(apicalling_info)
        if not flag:  # base check error!
            self.conv.add_message(m, role=Role.SYSTEM)
            prediction = APIOutput(
                name=apicalling_info.action,
                request=apicalling_info.action_input,
                response_data=m,
                response_status_code=404,
            )
        else:
            self.cnt_api_callings[apicalling_info.action] += 1  # stat

            prompt = self._gen_prompt(apicalling_info)
            llm_response = self.llm.query_one(prompt)
            prediction = self.parse_react_output(llm_response, apicalling_info)
            if prediction.response_status_code == 200:
                msg_content = f"<API response> {prediction.response_data}"
            else:
                msg_content = f"<API response> {prediction.response_status_code} {prediction.response_data}"
            self.conv.add_message(
                msg_content,
                llm_name=self.cfg.api_llm_name,
                llm_prompt=prompt,
                llm_response=llm_response,
                role=Role.SYSTEM,
            )
        return prediction

    def _check_validation(self, apicalling_info: BotOutput) -> bool:
        # ... match the api by name? check params?
        api_names = [api["name"] for api in self.api_infos]
        if apicalling_info.action not in api_names:
            return (
                False,
                f"<Calling API Error> : {apicalling_info.action} not in {api_names}",
            )
        return True, None

    def _gen_prompt(self, apicalling_info: BotOutput) -> str:
        prompt = jinja_render(
            self.api_template_fn,  # "flowagent/api_llm.jinja": api_infos, api_name, api_input
            api_infos=self.api_infos,
            api_name=apicalling_info.action,
            api_input=apicalling_info.action_input,
        )
        return prompt

    @staticmethod
    def parse_json_output(s: str, apicalling_info: BotOutput) -> APIOutput:
        """DEPRECATED!
        parse the output: status_code, data
        NOTE: can also output in the format of ReAct
        """
        if "```" in s:
            s = Formater.parse_codeblock(s, type="json")
        response = json.loads(s)  # eval | NameError: name 'null' is not defined
        assert all(key in response for key in ["status_code", "data"]), f"Response not in prediction: {s}"
        # parse the "data"?
        return APIOutput(
            name=apicalling_info.action,
            request=apicalling_info.action_input,
            response_data=response["data"],
            response_status_code=int(response["data"]),
        )

    @staticmethod
    def parse_react_output(s: str, apicalling_info: BotOutput) -> APIOutput:
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(?P<field>Status Code|Data):\s*(?P<value>.*?)(?=\n(Status Code|Data):|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group("field"): match.group("value").strip() for match in matches}

        # validate result
        assert all(key in result for key in ["Status Code", "Data"]), f"Data/Status Code not in prediction: {s}"
        return APIOutput(
            name=apicalling_info.action,
            request=apicalling_info.action_input,
            response_data=json.dumps(result["Data"], ensure_ascii=False),
            response_status_code=int(result["Status Code"]),
        )
