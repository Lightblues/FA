""" 
@241211
- [x] #feat implement UISingleBot
    modify from `ui_con/bot_single.py`.
    - replace streamlit with class properties
"""

import re, datetime, json
from .react_bot import ReactBot
from ...data import BotOutput, BotOutputType
from ...utils import jinja_render, OpenAIClient, Formater

class UISingleBot(ReactBot):
    """ 
    Usage::

        bot = UISingleBot(cfg=cfg, conv=conv, workflow=workflow)
        prompt, stream = bot.process_stream()
        llm_response = _process_stream(stream)
        bot_output = bot.process_LLM_response(prompt, llm_response)

    Used config:
        bot_llm_name
        ui_bot_template_fn <- bot_template_fn
        bot_retry_limit
    """
    # llm: OpenAIClient = None
    # bot_template_fn: str = "flowagent/bot_pdl.jinja"
    names = ["UISingleBot", "ui_single_bot"]

    def __init__(self, **args):
        super().__init__(**args)

    def _gen_prompt(self) -> str:
        # TODO: format apis. 1) remove URL; 2) add preconditions
        state_infos = {
            "Current time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        # s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."
        state_infos |= self.workflow.pdl.status_for_prompt # add the status infos from PDL!
        prompt = jinja_render(
            self.cfg.ui_bot_template_fn,       # "flowagent/bot_pdl.jinja"
            workflow_name=self.workflow.pdl.Name, # 
            PDL=self.workflow.pdl.to_str_wo_api(),  # .to_str()
            api_infos=self.workflow.toolbox,
            conversation=self.conv.to_str(),
            user_additional_constraints = self.cfg.ui_user_additional_constraints,
            current_state="\n".join(f"{k}: {v}" for k,v in state_infos.items()),
        )
        return prompt
    
    def process_LLM_response(self, prompt: str, llm_response:str) -> BotOutput:
        prediction = self._parse_react_output(llm_response)
        
        if prediction.action:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        elif prediction.response:
            msg_content = prediction.response
        else: raise NotImplementedError
        self.conv.add_message(msg_content, llm_name=self.cfg.ui_bot_llm_name, llm_prompt=prompt, llm_response=llm_response, role="bot_main")
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
            thought = result.get("Thought", "")
            action = action_input = None
            if "Action" in result:        # Action
                action = result["Action"]
                if action:
                    if action.startswith("API_"): action = action[4:]
                    action_input = json.loads(result["Action Input"]) # eval: NameError: name 'null' is not defined
            response = result.get("Response", "")
            return BotOutput(action=action, action_input=action_input, response=response, thought=thought)
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {s}\n[Result] {result}")