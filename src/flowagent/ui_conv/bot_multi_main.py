import datetime, json, re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import streamlit as st; ss = st.session_state

from ..data import Config, Message, Conversation, BotOutput, Role, BotOutputType, DataManager
from ..utils import jinja_render, OpenAIClient, Formater, init_client, LLM_CFG
# from ..roles import ReactBot
from .bot_single import PDL_UIBot
from ..tools import TOOL_SCHEMAS

@dataclass
class MainBotOutput:
    thought: str = None
    workflow: str = None # workflow name
    response: str = None
    action: str = None
    action_input: Dict = None


class Multi_Main_UIBot(PDL_UIBot):
    """Multi_Main_UIBot

    self: llm
    ss (session_state): cfg.[mui_agent_main_template_fn, mui_agent_main_llm_name], workflow, conv, user_additional_constraints

    Usage::
        bot = Multi_Main_UIBot()
        prompt, stream = bot.process_stream() # show the stream
        bot_output: BotOutput = bot.process_LLM_response(prompt, llm_response)
    """
    workflows: Dict[str, Dict] = field(default_factory=dict) # {"000": {name, task_description, task_detailed_description}}
    def __init__(self) -> None:
        # super().__init__()
        self.llm = init_client(llm_cfg=LLM_CFG[ss.cfg.mui_agent_main_llm_name])

    def refresh_config(self): # bot_template_fn
        self.__init__()
    
    def _gen_prompt(self) -> str:
        state_infos = {
            "Current time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        workflows = [w for w in ss.workflow_infos if w['is_activated']]
        _shown_keys = ["name", "task_description"]  # remove "task_detailed_description"
        workflows = [{k:v for k,v in w.items() if k in _shown_keys} for w in workflows]
        enabled_tools = [k for k,v in ss.tools.items() if v['is_enabled']]
        tools_info = [s for s in TOOL_SCHEMAS if s['function']['name'] in enabled_tools]
        prompt = jinja_render(
            ss.cfg.mui_agent_main_template_fn,       # "flowagent/bot_mui_main_agent.jinja"
            workflows=workflows,
            tools_info=tools_info,
            conversation=ss.conv.to_str(),
            current_state="\n".join(f"{k}: {v}" for k,v in state_infos.items()),
        )
        return prompt

    @staticmethod
    def _parse_react_output(s: str) -> MainBotOutput:
        """Parse output with full `Tought, Workflow, Response`."""
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        # pattern = r"(Thought|Workflow|Response):\s*(.*?)\s*(?=Thought:|Workflow:|Response:|\Z)"
        pattern = r"(Thought|Workflow|Action|Action Input|Response):\s*(.*?)\s*(?=Thought:|Workflow:|Action:|Action Input:|Response:|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group(1): match.group(2).strip() for match in matches}
        print(f"> result: {result}")

        # validate result
        try:
            thought = result.get("Thought", "")
            workflow = result.get("Workflow", "")
            response = result.get("Response", "")
            if ("Action" in result) and result['Action']:
                action = result['Action']
                if action.startswith("API_"): action = action[4:]
                action_input = Formater.parse_json_or_eval(result['Action Input'])
            else: action, action_input = "", {}
            # return MainBotOutput(workflow=workflow, response=response, thought=thought)
            return MainBotOutput(workflow=workflow, response=response, thought=thought, action=action, action_input=action_input)
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {s}\n[Result] {result}")

    def process_LLM_response(self, prompt: str, llm_response:str) -> MainBotOutput:
        prediction = self._parse_react_output(llm_response)

        if prediction.workflow:
            msg_content = f"<Call workflow> {prediction.workflow}"
        else:
            if prediction.action:
                msg_content = f"<Call Tool> {prediction.action}({prediction.action_input})"
            elif prediction.response:
                msg_content = prediction.response
            else: raise NotImplementedError
        self._add_message(msg_content, prompt=prompt, llm_response=llm_response, role="bot_main")
        return prediction
