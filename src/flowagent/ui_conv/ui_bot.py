""" 
@240718 从 engine_v1.bots 进行修改

- [ ] add refresh api
    def refresh_conversation / refresh_workflow
"""

import datetime, json
from typing import List, Dict, Optional, Tuple

from ..data import Config, Message, Conversation, BotOutput, Role, BotOutputType
from ..utils import jinja_render, OpenAIClient
from ..roles import ReactBot


class PDL_UIBot(ReactBot):
    ui_bot_template_fn: str = "flowagent/bot_pdl_ui.jinja"
    def __init__(self, **args) -> None:
        super().__init__(**args)
        if self.cfg.ui_bot_template_fn is not None: self.ui_bot_template_fn = self.cfg.ui_bot_template_fn
    
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
            self.ui_bot_template_fn,       # "flowagent/bot_pdl.jinja"
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
