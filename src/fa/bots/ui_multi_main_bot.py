"""
@241211
- [x] #feat implement UIMultiMainBot
    modify from `ui_con/bot_multi_main.py`:
"""

import re
from typing import Dict, List

from common import (
    LLM_CFG,
    Formater,
    PromptUtils,
    init_client,
    jinja_render,
)
from data import DataManager, MainBotOutput
from tools import TOOL_SCHEMAS, TOOLS_MAP

from .react_bot import ReactBot


class UIMultiMainBot(ReactBot):
    """UIMultiMainBot

    self: llm
    ss (session_state): cfg.[mui_agent_main_template_fn, mui_agent_main_llm_name], workflow, conv

    Usage::

        bot = UIMultiMainBot()
        prompt, stream = bot.process_stream()  # show the stream
        bot_output: BotOutput = bot.process_LLM_response(prompt, llm_response)
    """

    # cfg: Config = None
    # conv: Conversation = None
    # llm: OpenAIClient = None
    tools: Dict[str, Dict] = {}
    bot_main_workflow_infos: List[Dict] = []  # [{name, task_description, task_detailed_description}]
    names = ["UIMultiMainBot", "ui_multi_main_bot"]

    def __init__(self, workflow_infos: List[Dict] = None, **args):
        # logger.info(f"init UIMultiMainBot with workflow_infos: {workflow_infos}")
        super().__init__(**args)
        # use `config.mui_agent_main_llm_name`
        self.llm = init_client(llm_cfg=LLM_CFG[self.cfg.mui_agent_main_llm_name])
        self._init_workflow_infos(workflow_infos)
        self._init_tools()

    def _init_workflow_infos(self, workflow_infos: List[Dict] = []):  # config.workflow_infos
        # 1. set default workflow_infos
        if not workflow_infos:
            workflow_infos = DataManager(self.cfg).workflow_infos.values()
            for w in workflow_infos:
                w["is_activated"] = True
        # if ss.cfg.mui_available_workflows:
        #     workflow_names = [w['name'] for w in ss.workflow_infos]
        #     assert all(w in workflow_names for w in ss.cfg.mui_available_workflows)
        #     ss.workflow_infos = [w for w in ss.workflow_infos if w['name'] in ss.cfg.mui_available_workflows]
        self.bot_main_workflow_infos = workflow_infos

    def _init_tools(self):
        tools = {}
        for t in self.cfg.ui_tools:
            assert t["name"] in TOOLS_MAP, f"{t['name']} not in available tools {TOOLS_MAP.keys()}"
            tools[t["name"]] = {
                "is_enabled": t.get("is_enabled", True),
            }
        self.tools = tools

    def _gen_prompt(self) -> str:
        state_infos = {
            "Current time": PromptUtils.get_formated_time(),
        }
        workflows = [w for w in self.bot_main_workflow_infos if w["is_activated"]]
        _shown_keys = ["name", "task_description"]  # remove "task_detailed_description"
        workflows = [{k: v for k, v in w.items() if k in _shown_keys} for w in workflows]
        enabled_tools = [k for k, v in self.tools.items() if v["is_enabled"]]
        tools_info = [s for s in TOOL_SCHEMAS if s["function"]["name"] in enabled_tools]
        prompt = jinja_render(
            self.cfg.mui_agent_main_template_fn,  # "flowagent/bot_mui_main_agent.jinja"
            workflows=workflows,
            tools_info=tools_info,
            conversation=self.conv.to_str(),
            current_state="\n".join(f"{k}: {v}" for k, v in state_infos.items()),
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
        # print(f"> result: {result}")

        # validate result
        try:
            thought = result.get("Thought", "")
            workflow = result.get("Workflow", "")
            response = result.get("Response", "")
            if ("Action" in result) and result["Action"]:
                action = result["Action"]
                if action.startswith("API_"):
                    action = action[4:]
                action_input = Formater.parse_json_or_eval(result["Action Input"])
            else:
                action, action_input = "", {}
            # return MainBotOutput(workflow=workflow, response=response, thought=thought)
            return MainBotOutput(
                workflow=workflow,
                response=response,
                thought=thought,
                action=action,
                action_input=action_input,
            )
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {s}\n[Result] {result}")

    def process_LLM_response(self, prompt: str, llm_response: str) -> MainBotOutput:
        prediction = self._parse_react_output(llm_response)

        if prediction.workflow:
            msg_content = f"<Call workflow> {prediction.workflow}"
        else:
            if prediction.action:
                msg_content = f"<Call Tool> {prediction.action}({prediction.action_input})"
            elif prediction.response:
                msg_content = prediction.response
            else:
                raise NotImplementedError
        self.conv.add_message(
            msg_content,
            llm_name=self.cfg.mui_agent_main_llm_name,
            llm_prompt=prompt,
            llm_response=llm_response,
            role="bot_main",
        )
        return prediction
