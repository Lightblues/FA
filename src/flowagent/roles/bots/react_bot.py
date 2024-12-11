import re, datetime, json
from typing import List, Tuple
from ..base import BaseBot
from ...data import BotOutput, BotOutputType, Message, Role, LogUtils
from ...utils import jinja_render, retry_wrapper, OpenAIClient, Formater, init_client, LLM_CFG


class ReactBot(BaseBot):
    """ ReactBot
    
    prediction format: 
        (Thought, Response) for response node 
        (Thought, Action, Action Input) for call api node

    Used config:
        bot_llm_name
        bot_template_fn
        bot_retry_limit
    """
    bot_template_fn: str = "flowagent/bot_flowbench.jinja"  # using the prompt from FlowBench
    names = ["ReactBot", "react_bot"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)

    def process(self, *args, **kwargs) -> BotOutput:
        """ mian process logic.
        gen prompt -> query & process -> gen message
        """
        # 1. (maybe) pre-decisions, see CoREBot
        # 2. query and parse LLM
        prompt = self._gen_prompt()
        @retry_wrapper(retry=self.cfg.bot_retry_limit, step_name="bot_process", log_fn=print)
        def process_with_retry(prompt):
            # todo: retry with random / search?
            llm_response, prediction = self._process(prompt)
            return llm_response, prediction
        llm_response, prediction = process_with_retry(prompt)  # prediction: BotOutput
        # 3. add message to conversation
        if prediction.response:
            msg_content = prediction.response
        else:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        self._add_message(msg_content, prompt=prompt, llm_response=llm_response)
        self.cnt_bot_actions += 1  # stat
        return prediction

    def _gen_prompt(self) -> str:
        prompt = jinja_render(
            self.bot_template_fn,     # "flowagent/bot_flowbench.jinja": task_description, workflow, toolbox, current_time, history_conversation
            task_description=self.workflow.task_description,
            workflow=self.workflow.workflow,
            toolbox=self.workflow.toolbox,
            current_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            history_conversation=self.conv.to_str(),
        )
        return prompt

    def _process(self, prompt:str=None) -> Tuple[str, BotOutput]:
        llm_response = self.llm.query_one(prompt)
        prediction = self.parse_react_output(llm_response)
        return llm_response, prediction
    
    @staticmethod
    def parse_react_output(s: str) -> BotOutput:
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(?P<field>Thought|Action|Action Input|Response):\s*(?P<value>.*?)(?=\n(Thought|Action|Action Input|Response):|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group('field'): match.group('value').strip() for match in matches}
        
        # validate result
        # assert "Thought" in result, f"Thought not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
        thought = result.get("Thought", "")
        if "Action" in result:        # Action
            assert "Action Input" in result, f"Action Input not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            try: # NOTE: ensure the input is in json format! 
                result["Action Input"] = json.loads(result["Action Input"]) # eval: NameError: name 'null' is not defined
            except Exception as e:
                raise RuntimeError(f"Action Input not in json format! LLM output:\n" + LogUtils.format_infos_basic(s))
            if result["Action"].startswith("API_"):
                result["Action"] = result["Action"][4:]
            output = BotOutput(action=result["Action"], action_input=result["Action Input"], thought=thought)
        else:
            assert "Response" in result, f"Response not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            output = BotOutput(response=result["Response"], thought=thought)
        return output