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
    """
    llm: OpenAIClient = None
    bot_template_fn: str = "flowagent/bot_flowbench.jinja"  # using the prompt from FlowBench
    names = ["ReactBot", "react_bot"]
    
    def __init__(self, **args) -> None:
        super().__init__(**args)
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.bot_llm_name])
        
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
        if prediction.action_type==BotOutputType.RESPONSE:
            msg_content = prediction.response
        else:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        msg = Message(
            Role.BOT, msg_content, prompt=prompt, llm_response=llm_response,
            conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
        )
        self.conv.add_message(msg)
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
        # assert BotOutput.thought_str in result, f"Thought not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
        thought = result.get(BotOutput.thought_str, "")
        if BotOutput.action_str in result:        # Action
            assert BotOutput.action_input_str in result, f"Action Input not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            try: # NOTE: ensure the input is in json format! 
                result[BotOutput.action_input_str] = json.loads(result[BotOutput.action_input_str]) # eval: NameError: name 'null' is not defined
            except Exception as e:
                raise RuntimeError(f"Action Input not in json format! LLM output:\n" + LogUtils.format_infos_basic(s))
            if result[BotOutput.action_str].startswith("API_"):
                result[BotOutput.action_str] = result[BotOutput.action_str][4:]
            output = BotOutput(action=result[BotOutput.action_str], action_input=result[BotOutput.action_input_str], thought=thought)
        else:
            assert BotOutput.response_str in result, f"Response not in prediction! LLM output:\n" + LogUtils.format_infos_basic(s)
            output = BotOutput(response=result[BotOutput.response_str], thought=thought)
        return output