""" 
@240718 从 engine_v1.bots 进行修改

- [x] add refresh api
    def refresh_conversation / refresh_workflow
"""

import datetime, json, re
from typing import List, Dict, Optional, Tuple, Union
import streamlit as st; ss = st.session_state

from ..data import Config, Message, Conversation, BotOutput, Role, BotOutputType
from ..utils import jinja_render, OpenAIClient, Formater, init_client, LLM_CFG
# from ..roles import ReactBot

class PDL_UIBot():
    """PDL_UIBot

    self: llm
    ss (session_state): cfg, workflow, conv, user_additional_constraints, bot_template_fn

    Usage::
        bot = PDL_UIBot()
        prompt, stream = bot.process_stream() # show the stream
        bot_output: BotOutput = bot.process_LLM_response(prompt, llm_response)
    """
    def __init__(self) -> None:
        # super().__init__(**args)
        self.llm = init_client(llm_cfg=LLM_CFG[ss.cfg.bot_llm_name])
    
    def refresh_config(self): # bot_template_fn
        self.__init__()
    
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
        state_infos |= ss.workflow.pdl.status_for_prompt # add the status infos from PDL!
        prompt = jinja_render(
            ss.cfg.bot_template_fn,       # "flowagent/bot_pdl.jinja"
            workflow_name=ss.curr_status, # TODO: to be fixed
            PDL=ss.workflow.pdl.to_str_wo_api(),  # .to_str()
            api_infos=ss.workflow.toolbox,
            conversation=ss.conv.to_str(),
            user_additional_constraints = ss.user_additional_constraints,
            current_state="\n".join(f"{k}: {v}" for k,v in state_infos.items()),
        )
        return prompt

    def process_LLM_response(self, prompt: str, llm_response:str) -> BotOutput:
        prediction = self._parse_react_output(llm_response)
        
        if prediction.action_type==BotOutputType.RESPONSE:
            msg_content = prediction.response
        elif prediction.action_type==BotOutputType.ACTION:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        else: raise NotImplementedError
        self._add_message(msg_content, prompt=prompt, llm_response=llm_response)
        return prediction

    @staticmethod
    def _parse_react_output(s: str) -> BotOutput:
        """Parse output with full `Tought, Action, Action Input, Response`."""
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
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

    def _add_message(self, msg_content: str, prompt: str=None, llm_response:str=None, role:Union[Role, str]=Role.BOT):
        msg = Message(
            role, msg_content, prompt=prompt, llm_response=llm_response,
            conversation_id=ss.conv.conversation_id, utterance_id=ss.conv.current_utterance_id
        )
        ss.conv.add_message(msg)