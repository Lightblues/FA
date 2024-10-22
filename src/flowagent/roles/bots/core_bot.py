
import re, datetime, json
from typing import List, Tuple
from .react_bot import ReactBot
from ...data import BotOutput, BotOutputType
from ...data.core import CoreFlow, CoreBlock
from ...utils import jinja_render, OpenAIClient

class CoREBot(ReactBot):
    """ 
    Use the react format for action prediction
    """
    llm: OpenAIClient = None
    bot_template_fn: str = "flowagent/bot_core.jinja"
    names = ["CoREBot", "core_bot"]
    
    curr_block: CoreBlock = None
    
    def __init__(self, **args):
        super().__init__(**args)
        self.curr_block = self.workflow.core_flow.header
    
    def process(self, *args, **kwargs) -> BotOutput:
        """ use the branch jusmp logic in CoRE! """
        # 1. branching (update current block) based on previous action & env response
        if len(self.conv) > 1: # skip the first round! 
            if len(self.curr_block.branch) == 1:  # no branches
                self.curr_block = list(self.curr_block.branch.values())[0]
            else:
                branch = self.check_branch() # make decision based on current block (question) and env response
                if branch not in self.curr_block.branch: branch = list(self.curr_block.branch.keys())[0]
        # 1.2 terminate condition
        if (len(self.curr_block.branch) == 0) or (self.curr_block.type.lower() == "terminal"):
            return BotOutput()  # BotOutputType.END
        # 2. back to ReActBot
        return super().process(*args, **kwargs)
    
    def _gen_prompt(self) -> str:
        prompt = jinja_render(
            self.bot_template_fn,       # "flowagent/bot_core.jinja"
            task_description=self.workflow.task_description,
            api_infos=self.workflow.toolbox,
            conversation=self.conv.to_str(), 
            question=self.curr_block.get_instruction(), 
            # Process:::Inquire the user for the hospital name, department name, and appointment time
            # Decision:::Call check_hospital to verify the hospital name provided by the user
        )
        return prompt
    
    def _process(self, prompt:str=None) -> Tuple[str, BotOutput]:
        llm_response = self.llm.query_one(prompt)
        prediction = self.parse_react_output(llm_response)
        return llm_response, prediction
    
    def check_branch(self):
        possible_keys = list(self.curr_block.branch.keys())
        _possible_keys_str = "\n".join(f"{i+1}: {key}" for i, key in enumerate(possible_keys))
        prompt = f'Given the question ```{self.curr_block.get_instruction()}```, here are your action and response ```{self.conv[-2:]}```\n' \
            f'Choose one from the following options that best match current condition. \n{_possible_keys_str}\n' \
            f"Your answer should be only an number, referring to the desired choice. Don't be verbose!"
        response = self.llm.query_one(prompt, stop=['.'])
        if response.isdigit() and 1 <= int(response) <= len(possible_keys):
            response = int(response)
            return possible_keys[response - 1]
        else: return possible_keys[0]  # randomly pick one