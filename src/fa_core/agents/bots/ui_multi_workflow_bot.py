"""
@241211
- [x] #feat implement UIMultiWorkflowBot
    modify from `ui_con/bot_multi_workflow.py`:
"""

from fa_core.common import jinja_render, init_client
from fa_core.data import BotOutput

from .ui_single_bot import UISingleBot
from .bot_tools import tool_switch_main, tool_response


class UIMultiWorkflowBot(UISingleBot):
    """UIMultiWorkflowBot"""

    names = ["UIMultiWorkflowBot", "ui_multi_workflow_bot"]

    def _post_init(self) -> None:
        # 1. init the LLM client
        self.bot_template_fn = self.cfg.bot_template_fn or "bot_mui_workflow_agent.jinja"
        self.bot_llm_name = self.cfg.bot_llm_name
        self.llm = init_client(
            self.bot_llm_name,
            stop=["[END]"],
            **self.cfg.bot_llm_kwargs,
        )
        # 2. add the special tool "switch_main"
        self.context.workflow.pdl.add_tool(tool_switch_main)
        self.context.workflow.pdl.add_tool(tool_response)

    def _gen_prompt(self) -> str:
        workflow = self.context.workflow
        state_infos = self.context.status_for_prompt  # add the status infos from PDL!
        prompt = jinja_render(
            self.cfg.mui_agent_workflow_template_fn,
            workflow_name=workflow.pdl.Name,
            PDL=workflow.pdl.to_json(),
            api_infos=[tool.model_dump() for tool in workflow.pdl.tools],
            conversation=self.context.conv.to_str(),
            current_state=state_infos.to_str(),
        )
        return prompt

    def process_LLM_response(self) -> BotOutput:
        prediction = self._parse_react_output()

        if prediction.action:
            if prediction.action.startswith("workflow_"):
                msg_content = f"<Call workflow> {prediction.action.split('_',1)[1]}({prediction.action_input})"
            else:
                msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        elif prediction.response:
            msg_content = prediction.response
        else:
            raise RuntimeError("response is empty")
        self.context.conv.add_message(
            msg_content,
            llm_name=self.cfg.mui_agent_main_llm_name,
            llm_prompt=self.last_llm_prompt,
            llm_response=self.last_llm_response,
            role=f"bot_{self.context.workflow.name}",
        )
        return prediction
