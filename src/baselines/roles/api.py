""" updated @240906
- [ ] generate api response with given history calling infos
"""
from typing import List
from engine import Role, Message, init_client, LLM_CFG
from .base import BaseAPIHandler
from ..data import APIOutput, BotOutput
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater

class DummyAPIHandler(BaseAPIHandler):
    """ 
    API structure: (see apis_v0/apis.json)
    """
    names: List[str] = ["dummy_api"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.cnt_api_callings: int = 0
        
    def process(self, *args, **kwargs) -> APIOutput:
        """ 
        1. match and check the validity of API
        2. call the API (with retry?)
        3. parse the response
        """
        # raise NotImplementedError
        self.cnt_api_callings += 1
        
        self.conv.add_message(
            Message(role=Role.SYSTEM, content="api calling..."),
        )
        api_output = APIOutput()
        return api_output


class LLMSimulatedAPIHandler(BaseAPIHandler):
    llm: OpenAIClient = None
    names = ["llm", "LLMSimulatedAPIHandler"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.api_llm_name])
        
    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        # ... match the api by name? check params? 
        # TODO: integrate with FastAPI
        prompt = jinja_render(
            self.cfg.api_template_fn,     # "baselines/api_llm.jinja": api_infos, api_name, api_input
            api_infos=self.api_infos,
            api_name=apicalling_info.action,
            api_input=apicalling_info.action_input,
        )
        llm_response = self.llm.query_one(prompt)
        # ...parse the response! -> APIOutput, conv
        prediction = self.parse_api_output(llm_response, apicalling_info)
        if prediction.response_status_code==200:
            msg_content = f"<API response> {prediction.response_data}"
        else:
            msg_content = f"<API response> {prediction.response_status_code} {prediction.response_data}"
        msg = Message(
            Role.SYSTEM, msg_content, prompt=prompt, llm_response=llm_response, 
            conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
        )
        self.conv.add_message(msg)
        self.cnt_api_callings[prediction.name] += 1 # stat
        return prediction

    @staticmethod
    def parse_api_output(s:str, apicalling_info:BotOutput) -> APIOutput:
        """ 
        parse the output: status_code, data
        NOTE: can also output in the format of ReAct
        """
        if "```" in s:
            s = Formater.parse_codeblock(s, type="json")
        response = eval(s)
        assert all(key in response for key in [APIOutput.response_status_str, APIOutput.response_data_str]), f"Response not in prediction: {s}"
        # parse the "data"?
        return APIOutput(
            name=apicalling_info.action,
            request=apicalling_info.action_input,
            response_data=response[APIOutput.response_data_str],
            response_status_code=int(response[APIOutput.response_status_str]),
        )
