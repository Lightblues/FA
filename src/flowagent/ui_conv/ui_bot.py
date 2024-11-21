""" 
@240718 从 engine_v1.bots 进行修改

- [ ] add refresh api
    def refresh_conversation / refresh_workflow
"""

import datetime, json, re
from typing import List, Dict, Optional, Tuple

from ..data import Config, Message, Conversation, BotOutput, Role, BotOutputType
from ..utils import jinja_render, OpenAIClient, Formater
from ..roles import ReactBot


class PDL_UIBot(ReactBot):
    def __init__(self, **args) -> None:
        super().__init__(**args)
    
    def refresh_config(self, cfg: Config):
        """For UI, only update the config and bot_template_fn"""
        self.cfg = cfg
    
    def process_stream(self):
        prompt = self._gen_prompt()
        llm_response_stream = self.llm.query_one_stream_generator(prompt)
        return prompt, llm_response_stream

    def _gen_prompt(self) -> str:
        # TODO: format apis
        state_infos = {
            "Current time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        # s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."
        state_infos |= self.workflow.pdl.status_for_prompt # add the status infos from PDL!
        prompt = jinja_render(
            self.bot_template_fn,       # "flowagent/bot_pdl.jinja"
            PDL=self.workflow.pdl.to_str_wo_api(),  # .to_str()
            api_infos=self.workflow.toolbox,        # self.workflow.get_toolbox_by_names(valid_api_names),
            conversation=self.conv.to_str(),
            user_additional_constraints = self.cfg.ui_user_additional_constraints,
            current_state="\n".join(f"{k}: {v}" for k,v in state_infos.items()),
        )
        # print(f"Current pdl state: {self.workflow.pdl.status_for_prompt}")
        return prompt

    def process_LLM_response(self, prompt: str, llm_response:str) -> BotOutput:
        prediction = self.parse_react_output(llm_response)
        
        if prediction.action_type==BotOutputType.RESPONSE:
            msg_content = prediction.response
        else:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        msg = Message(
            Role.BOT, msg_content, prompt=prompt, llm_response=llm_response,
            conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id
        )
        self.conv.add_message(msg)
        return prediction

    @staticmethod
    def parse_react_output(s: str) -> BotOutput:
        """Parse output with full `Tought, Action, Action Input, Response`."""
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        # pattern = r"(?P<field>Thought|Action|Action Input|Response):\s*(?P<value>.*?)(?=\n(?:Thought|Action|Action Input|Response):|\Z)"
        # result = {match.group('field'): match.group('value').strip() for match in matches}
        pattern = r"(Thought|Action|Action Input|Response):\s*(.*?)\s*(?=Thought:|Action:|Action Input:|Response:|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group(1): match.group(2).strip() for match in matches}
        
        # validate result
        try:
            thought = result.get(BotOutput.thought_str, "")
            action = action_input = ""
            if BotOutput.action_str in result:        # Action
                action = result[BotOutput.action_str]
                if action:
                    if action.startswith("API_"): action = action[4:]
                    action_input = json.loads(result[BotOutput.action_input_str]) # eval: NameError: name 'null' is not defined
            response = result.get(BotOutput.response_str, "")
            return BotOutput(action=action, action_input=action_input, response=response, thought=thought)
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {s}\n[Result] {result}")
