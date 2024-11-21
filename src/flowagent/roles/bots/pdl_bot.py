import re, datetime, json
from typing import List, Tuple
from .react_bot import ReactBot
from ...data import BotOutput, BotOutputType
from ...utils import jinja_render, OpenAIClient

class PDLBot(ReactBot):
    """ 
    Use the react format for action prediction
    """
    llm: OpenAIClient = None
    bot_template_fn: str = "flowagent/bot_pdl.jinja"
    names = ["PDLBot", "pdl_bot"]
    
    def __init__(self, **args):
        super().__init__(**args)
    
    def _gen_prompt(self) -> str:
        state_infos = {
            "Current time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        state_infos |= self.workflow.pdl.status_for_prompt # NOTE: add the status infos from PDL!
        # TODO: format apis
        prompt = jinja_render(
            self.bot_template_fn,       # "flowagent/bot_pdl.jinja"
            api_infos=self.workflow.toolbox,        # self.workflow.get_toolbox_by_names(valid_api_names),
            PDL=self.workflow.pdl.to_str_wo_api(),  # .to_str()
            conversation=self.conv.to_str(), 
            current_state="\n".join(f"{k}: {v}" for k,v in state_infos.items()),
        )
        # print(f"  Current pdl state: {self.workflow.pdl.status_for_prompt}")
        return prompt
    
    def _process(self, prompt:str=None) -> Tuple[str, BotOutput]:
        llm_response = self.llm.query_one(prompt)
        # transform json -> react format? 
        prediction = self.parse_react_output(llm_response)
        return llm_response, prediction
    
    # @staticmethod
    # def parse_json_output(s: str) -> BotOutput:
    #     parsed_response = Formater.parse_llm_output_json(s)
    #     assert "action_type" in parsed_response, f"parsed_response: {parsed_response}"
    #     action_type = ActionType[parsed_response["action_type"]]
    #     action_metas = APICalling_Info(name=action_name, kwargs=action_parameters)
    