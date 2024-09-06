""" updated 240905
"""
import re, datetime
from typing import List
from engine import Message, Role, init_client, LLM_CFG
from .base import BaseBot
from ..data import BotOutput, BotOutputType
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater

class DummyBot(BaseBot):
    names: List[str] = ["dummy_bot"]
    
    # def __init__(self, **args) -> None:
    #     super().__init__(**args)

    def process(self, *args, **kwargs) -> BotOutput:
        """ 
        1. generate ReAct format output by LLM
        2. parse to BotOutput
        """
        self.cnt_bot_actions += 1
        
        if (self.cnt_bot_actions % 2) == 0:
            bot_output = BotOutput(action="calling api!")
            self.conv.add_message(
                Message(role=Role.BOT, content="bot action..."),
            )
        else:
            bot_output = BotOutput(response="bot response...")
            self.conv.add_message(
                Message(role=Role.BOT, content="bot response..."),
            )
        return bot_output
    
    
class ReactBot(BaseBot):
    llm: OpenAIClient = None
    names = ["react", "ReactBot", "react_bot"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.bot_llm_name])
        
    def process(self, *args, **kwargs) -> BotOutput:
        prompt = jinja_render(
            self.cfg.bot_template_fn,     # "baselines/flowbench.jinja": task_background, workflow, toolbox, current_time
            task_background=self.workflow.task_background,
            workflow=self.workflow.workflow,
            toolbox=self.workflow.toolbox,
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            history_conversation=self.conv.to_str(),
        )
        llm_response = self.llm.query_one(prompt)
        # ...parse the response! -> BotOutput, conv
        prediction = self.parse_react_output(llm_response)
        if prediction.action_type==BotOutputType.RESPONSE:
            msg_content = prediction.response
        else:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        msg = Message(Role.BOT, msg_content, prompt=prompt, llm_response=llm_response)
        self.conv.add_message(msg)
        self.cnt_bot_actions += 1  # stat
        return prediction
        
    @staticmethod
    def parse_react_output(s: str) -> BotOutput:
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        # pattern = r"(Thought|Action|Action Input|Response):\s*(.*?)(?=\n\w+:|\Z)"
        # matches = re.findall(pattern, s, re.DOTALL)
        # result = {key: value.strip() for key, value in matches}
        pattern = r"(?P<field>Thought|Action|Action Input|Response):\s*(?P<value>.*?)(?=\n(Thought|Action|Action Input|Response):|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group('field'): match.group('value').strip() for match in matches}
        
        # validate result
        assert BotOutput.thought_str in result, f"Thought not in prediction: {s}"
        if BotOutput.action_str in result:        # Action
            assert BotOutput.action_input_str in result, f"Action Input not in prediction: {s}"
            result[BotOutput.action_input_str] = eval(result[BotOutput.action_input_str])
            output = BotOutput(action=result[BotOutput.action_str], action_input=result[BotOutput.action_input_str], thought=result[BotOutput.thought_str])
        else:
            assert BotOutput.response_str in result, f"Response not in prediction: {s}"
            output = BotOutput(response=result[BotOutput.response_str], thought=result[BotOutput.thought_str])
        return output