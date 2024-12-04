import datetime, json, re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import streamlit as st; ss = st.session_state

from ..utils import jinja_render, OpenAIClient, Formater, init_client, LLM_CFG
from .bot_single import PDL_UIBot

@dataclass
class WorkflowBotOutput:
    thought: str = None
    workflow: str = None # workflow name
    response: str = None
    action: str = None                      # api name
    action_input: Dict = None               # api paras. deprecated: Union[str, Dict]
    
    # TODO: enable response + action simultaneously
    # @property
    # def action_type(self) -> BotOutputType:
    #     if self.workflow:
    #         return BotOutputType.SWITCH
    #     elif self.response:
    #         return BotOutputType.RESPONSE
    #     else:
    #         return BotOutputType.END

class Multi_Workflow_UIBot(PDL_UIBot):
    """Multi_Workflow_UIBot

    self: llm
    ss (session_state): 
        cfg.[mui_agent_workflow_template_fn, mui_agent_main_llm_name], 
        conv, 
        curr_workflow.[pdl]

    Usage::
        bot = Multi_Workflow_UIBot()
        prompt, stream = bot.process_stream() # show the stream
        bot_output: BotOutput = bot.process_LLM_response(prompt, llm_response)
    """
    def __init__(self) -> None:
        # super().__init__()
        self.llm = init_client(llm_cfg=LLM_CFG[ss.cfg.mui_agent_main_llm_name]) 

    def refresh_llm(self, llm_name: str):
        print(f"> refreshing llm to {llm_name}")
        self.llm = init_client(llm_cfg=LLM_CFG[llm_name])

    def refresh_config(self):
        self.__init__()
    
    def _gen_prompt(self) -> str:
        state_infos = {
            "Current time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        state_infos |= ss.curr_workflow.pdl.status_for_prompt # add the status infos from PDL!
        prompt = jinja_render(
            ss.cfg.mui_agent_workflow_template_fn,       # "flowagent/bot_pdl.jinja"
            workflow_name=ss.curr_status,
            PDL=ss.curr_workflow.pdl.to_str_wo_api(),  # .to_str()
            api_infos=ss.curr_workflow.toolbox,
            conversation=ss.conv.to_str(),
            current_state="\n".join(f"{k}: {v}" for k,v in state_infos.items()),
        )
        return prompt

    @staticmethod
    def _parse_react_output(s: str) -> WorkflowBotOutput:
        """Parse output with full `Tought, Workflow, Response`."""
        if "```" in s:
            s = Formater.parse_codeblock(s, type="").strip()
        pattern = r"(Thought|Workflow|Action|Action Input|Response):\s*(.*?)\s*(?=Thought:|Workflow:|Action:|Action Input:|Response:|\Z)"
        matches = re.finditer(pattern, s, re.DOTALL)
        result = {match.group(1): match.group(2).strip() for match in matches}
        
        # validate result
        try:
            print(f"> result: {result}")
            thought = result.get("Thought", "")
            workflow = result.get("Workflow", "")
            response = result.get("Response", "")
            if ("Action" in result) and result['Action']:
                action = result['Action']
                if action.startswith("API_"): action = action[4:]
                action_input = json.loads(result['Action Input'])
            else: action, action_input = "", {}
            return WorkflowBotOutput(workflow=workflow, response=response, thought=thought, action=action, action_input=action_input)
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {s}\n[Result] {result}")

    def process_LLM_response(self, prompt: str, llm_response:str) -> WorkflowBotOutput:
        prediction = self._parse_react_output(llm_response)
        
        if prediction.workflow:
            msg_content = f"<Call workflow> {prediction.workflow}"
        else:
            if prediction.action:
                msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
            elif prediction.response:
                msg_content = prediction.response
            else: raise NotImplementedError
        self._add_message(msg_content, prompt=prompt, llm_response=llm_response, role=f"bot_{ss.curr_status}")
        return prediction
