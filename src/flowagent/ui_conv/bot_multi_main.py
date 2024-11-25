import datetime, json, re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import streamlit as st; ss = st.session_state

from ..data import Config, Message, Conversation, BotOutput, Role, BotOutputType, DataManager
from ..utils import jinja_render, OpenAIClient, Formater
# from ..roles import ReactBot
from .bot_single import PDL_UIBot

@dataclass
class MainBotOutput:
    thought: str = None
    workflow: str = None # workflow name
    response: str = None
    
    @property
    def action_type(self) -> BotOutputType:
        if self.workflow:
            return BotOutputType.ACTION
        elif self.response:
            return BotOutputType.RESPONSE
        else:
            return BotOutputType.END

class Multi_Main_UIBot(PDL_UIBot):
    """Multi_Main_UIBot

    self: llm
    ss (session_state): cfg, workflow, conv, user_additional_constraints, mui_bot_template_fn

    Usage::
        bot = Multi_Main_UIBot()
        prompt, stream = bot.process_stream() # show the stream
        bot_output: BotOutput = bot.process_LLM_response(prompt, llm_response)
    """
    workflows: Dict[str, Dict] = field(default_factory=dict) # {"000": {name, task_description, task_detailed_description}}
    def __init__(self) -> None:
        super().__init__()
        self._build_workflows()
    def _build_workflows(self):
        self.workflows = ss.data_manager.workflow_infos
    
    def refresh_config(self): # bot_template_fn
        pass
    
    def _gen_prompt(self) -> str:
        state_infos = {
            "Current time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        # TODO: select available workflows (cfg.mui_available_workflows)
        prompt = jinja_render(
            ss.cfg.mui_bot_template_fn,       # "flowagent/bot_ui_main_agent.jinja"
            workflows=self.workflows,
            conversation=ss.conv.to_str(),
            current_state="\n".join(f"{k}: {v}" for k,v in state_infos.items()),
        )
        return prompt

    @staticmethod
    def _parse_react_output(s: str) -> MainBotOutput:
        """Parse output with full `Tought, Workflow, Response`."""
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(Thought|Workflow|Response):\s*(.*?)\s*(?=Thought:|Workflow:|Response:|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group(1): match.group(2).strip() for match in matches}
        
        # validate result
        try:
            thought = result.get("Thought", "")
            workflow = result.get("Workflow", "")
            response = result.get("Response", "")
            return MainBotOutput(workflow=workflow, response=response, thought=thought)
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {s}\n[Result] {result}")
