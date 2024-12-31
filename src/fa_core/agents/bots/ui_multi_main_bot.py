"""
@241211
- [x] #feat implement UIMultiMainBot
    modify from `ui_con/bot_multi_main.py`:
@241230
- [ ] tool_call mode for `UIMultiMainBot`
    - [ ] #tool wrap the `response_to_user` tool
    - [ ] #tool add a tool to call the workflow
"""

from typing import Dict, List, Iterator
from loguru import logger

from fa_core.common import init_client, jinja_render
from fa_core.data import FADataManager, BotOutput
from fa_core.tools import TOOL_SCHEMAS, TOOLS_MAP
from fa_core.data.pdl.tool import ToolSpec, ToolDefinition
from fa_core.agents.bots.bot_tools import tool_response

from .ui_single_bot import UISingleBot


class UIMultiMainBot(UISingleBot):
    """UIMultiMainBot

    self: llm
    ss (session_state): cfg.[bot_template_fn, bot_llm_name], workflow, conv

    Usage::

        bot = UIMultiMainBot()
        prompt, stream = bot.process_stream()  # show the stream
        bot_output: BotOutput = bot.process_LLM_response(prompt, llm_response)
    """

    names = ["UIMultiMainBot", "ui_multi_main_bot"]

    tool_status: Dict[str, Dict] = {}
    tool_definitions: Dict[str, ToolDefinition] = {}
    bot_main_workflow_infos: List[Dict] = []  # [{name, task_description}]

    def _post_init(self) -> None:
        self.bot_template_fn = self.cfg.bot_template_fn or "bot_mui_main_agent.jinja"
        self.bot_llm_name = self.cfg.bot_llm_name
        self.llm = init_client(
            self.bot_llm_name,
            stop=["[END]"],
            **self.cfg.bot_llm_kwargs,
        )
        self._init_workflow_infos(self.cfg.mui_workflow_infos)
        self._init_tools(self.cfg.ui_tools)
        logger.info(
            f"initialized UIMultiMainBot with {self.bot_llm_name} - {self.bot_template_fn}!\n bot_main_workflow_infos: {self.bot_main_workflow_infos}\n  tool_status: {self.tool_status}"
        )

    def _init_workflow_infos(self, workflow_infos: List[Dict] = []):
        if not workflow_infos:
            workflow_infos = FADataManager.get_workflow_infos(self.cfg.workflow_dataset).values()
            for w in workflow_infos:
                w["is_activated"] = True
        self.bot_main_workflow_infos = workflow_infos

    def _init_tools(self, tools_list: List[Dict]):
        # 1. "API" tools
        self.tool_definitions = TOOL_SCHEMAS
        for t in tools_list:
            assert t["name"] in TOOLS_MAP, f"{t['name']} not in available tools {TOOLS_MAP.keys()}"
            self.tool_status[t["name"]] = {"is_enabled": t.get("is_enabled", True)}
        # 2. "response_to_user" tool
        self.tool_status["response_to_user"] = {"is_enabled": True}
        self.tool_definitions["response_to_user"] = tool_response
        # 3. "call_workflow" tool
        workflows = [w for w in self.bot_main_workflow_infos if w["is_activated"]]
        for w in workflows:
            _tool_name = f"workflow_{w['name']}"
            tool_definition = ToolDefinition(
                type="function",
                function={
                    "name": _tool_name,
                    "description": w["task_description"],
                    "parameters": {},
                },
            )
            self.tool_definitions[_tool_name] = tool_definition
            self.tool_status[_tool_name] = {"is_enabled": True}

    def _gen_prompt(self) -> str:
        # 1. workflows
        workflows = [w for w in self.bot_main_workflow_infos if w["is_activated"]]
        workflows = [{k: v for k, v in w.items() if k in ["name", "task_description"]} for w in workflows]
        # 2. tools
        tools_info = [self.tool_definitions[k].model_dump() for k in self.tool_status if self.tool_status[k]["is_enabled"]]
        # 3. state
        state_infos = self.context.status_for_prompt
        prompt = jinja_render(
            self.bot_template_fn,
            workflows=workflows,
            tools_info=tools_info,
            conversation=self.context.conv.to_str(),
            current_state=state_infos.to_str(),
        )
        return prompt

    def process_stream(self) -> Iterator[str]:
        # reuse the stream from UISingleBot, only change the prompt
        return super().process_stream()

    def process_LLM_response(self) -> BotOutput:
        prediction = self._parse_react_output()

        # TODO: tune the message content
        if prediction.action:
            if prediction.action.startswith("workflow_"):
                msg_content = f"<Call workflow> {prediction.action.split('_', 1)[1]}"
            else:
                msg_content = f"<Call Tool> {prediction.action}({prediction.action_input})"
        elif prediction.response:
            msg_content = prediction.response
        else:
            raise RuntimeError("response is empty")
        self.context.conv.add_message(
            msg_content,
            llm_name=self.bot_llm_name,
            llm_prompt=self.last_llm_prompt,  # generated in process_stream
            llm_response=self.last_llm_response,  # generated in _parse_react_output
            role="bot_main",
        )
        return prediction
