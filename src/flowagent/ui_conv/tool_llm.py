import streamlit as st; ss = st.session_state
from ..roles.tools.llm_simulated_tool import LLMSimulatedTool
from ..utils import jinja_render, retry_wrapper, OpenAIClient, Formater, init_client, LLM_CFG
from ..data import APIOutput, BotOutput, Role, Message

class LLM_UITool(LLMSimulatedTool):
    """LLM_UITool

    Variables:
        self: llm, api_template_fn
        ss: conv, api_infos

    """
    names = ["llm_ui", "LLM_UITool"]
    llm: OpenAIClient = None
    api_template_fn: str = "flowagent/api_llm.jinja"
    
    def __init__(self):
        self.llm = init_client(llm_cfg=LLM_CFG[ss.cfg.api_llm_name])

    def process(self, apicalling_info: BotOutput, *args, **kwargs) -> APIOutput:
        flag, m = self._check_validation(apicalling_info)
        if not flag:        # base check error!
            self.conv.add_message(m, role=Role.SYSTEM)
            prediction = APIOutput(name=apicalling_info.action, request=apicalling_info.action_input, response_data=m, response_status_code=404)
        else:
            prompt = self._gen_prompt(apicalling_info)
            llm_response = self.llm.query_one(prompt)
            prediction = self.parse_react_output(llm_response, apicalling_info)
            if prediction.response_status_code==200:
                msg_content = f"<API response> {prediction.response_data}"
            else:
                msg_content = f"<API response> {prediction.response_status_code} {prediction.response_data}"
            self.conv.add_message(msg_content, llm_name=self.cfg.api_llm_name, llm_prompt=prompt, llm_response=llm_response, role=Role.SYSTEM)
        return prediction
    
    def _check_validation(self, apicalling_info: BotOutput) -> bool:
        # ... match the api by name? check params? 
        api_names = [api["name"] for api in ss.curr_workflow.toolbox]
        if apicalling_info.action not in api_names: 
            return False, f"<Calling API Error> : {apicalling_info.action} not in {api_names}"
        return True, None
    
    def _gen_prompt(self, apicalling_info: BotOutput) -> str:
        prompt = jinja_render(
            self.api_template_fn,     # "flowagent/api_llm.jinja": api_infos, api_name, api_input
            api_infos=ss.curr_workflow.toolbox,
            api_name=apicalling_info.action,
            api_input=apicalling_info.action_input,
        )
        return prompt