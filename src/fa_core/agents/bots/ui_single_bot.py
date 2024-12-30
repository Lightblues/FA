"""
@241211
- [x] #feat implement UISingleBot
    modify from `ui_con/bot_single.py`.
    - replace streamlit with class properties
@241220
- [x] rewrite roles with `pydantic`
    - [x] fix: roles
    - [x] fix: controllers (testing)
- [x] #feat add `Context`
@241230
- [x] #feat move `user_additional_constraints` to `status_for_prompt`

todos
- [ ] try seperate Procedure from PDL in prompt!
"""

import json
from typing import Iterator, List, Tuple, Union

from openai.types.chat.chat_completion_chunk import ChoiceDelta

from fa_core.common import Formater, init_client, jinja_render
from fa_core.data import BotOutput

from .base_bot import BaseBot
from .bot_tools import tool_response
from .re_utils import re_parse_react_output


class UISingleBot(BaseBot):
    """
    Usage::

        bot = UISingleBot(cfg=cfg, conv=conv, workflow=workflow)
        prompt, stream = bot.process_stream()
        llm_response = _process_stream(stream)
        bot_output = bot.process_LLM_response(prompt, llm_response)

    Used config:
        bot_llm_name
        bot_template_fn
        bot_retry_limit (for the .process() method)
    """

    names = ["UISingleBot", "ui_single_bot"]

    last_llm_chat_completions: List[ChoiceDelta] = []
    last_llm_prompt: str = ""  # the prompt for logging
    last_llm_response: str = ""  # the llm response (with tool calls) for logging

    def _post_init(self) -> None:
        kwargs = {"seed": 42, "temperature": 0.0}
        self.bot_template_fn = self.cfg.bot_template_fn
        self.bot_llm_name = self.cfg.bot_llm_name
        self.llm = init_client(
            self.bot_llm_name,
            stop=["[END]"],
            **kwargs,
        )

        self.context.workflow.pdl.add_tool(tool_response)  # NOTE: add "response_to_user" as a special tool!

        # add user's additional constraints from UI
        if self.cfg.ui_user_additional_constraints:
            self.context.status_for_prompt.user_additional_constraints = self.cfg.ui_user_additional_constraints

    def _gen_prompt(self) -> str:
        # - [x]: format apis
        data_handler = self.context.workflow
        state_infos = self.context.status_for_prompt  # add the status infos from PDL!
        _tool_infos = [tool.model_dump() for tool in data_handler.pdl.tools]
        # _pdl_info = data_handler.pdl.to_str()
        _pdl_info = data_handler.pdl.to_json()  # NOTE: convert to json instead of str!!
        prompt = jinja_render(
            self.bot_template_fn,
            workflow_name=data_handler.pdl.Name,
            PDL=_pdl_info,
            api_infos=_tool_infos,
            conversation=self.context.conv.to_str(),
            current_state=state_infos.to_str(),
        )
        return prompt

    def process_stream(self) -> Iterator[str]:
        self.last_llm_prompt = self._gen_prompt()
        response = self.llm.chat_completions_create(query=self.last_llm_prompt, stream=True)
        self.last_llm_chat_completions = []
        return self.llm.stream_generator(response, collected_deltas=self.last_llm_chat_completions)

    def process_LLM_response(self) -> BotOutput:
        prediction = self._parse_react_output()

        if prediction.action:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        elif prediction.response:
            msg_content = prediction.response
        else:
            raise RuntimeError("response is empty")
        self.context.conv.add_message(
            msg_content,
            llm_name=self.bot_llm_name,
            llm_prompt=self.last_llm_prompt,
            llm_response=self.last_llm_response,
            role="bot",
        )
        return prediction

    def _parse_react_output(self) -> BotOutput:
        """Parse output with full `Tought, Action, Action Input`."""
        llm_response = "".join(c.content or "" for c in self.last_llm_chat_completions)
        self.last_llm_response = llm_response
        if "```" in llm_response:
            llm_response = Formater.parse_codeblock(llm_response, type="").strip()
        result = re_parse_react_output(llm_response)

        # validate result
        try:
            assert all(k in result for k in ["Action", "Action Input"])
            thought = result.get("Thought", "")
            action, action_input = result["Action"], result["Action Input"]
            action_input = json.loads(action_input)  # eval: NameError: name 'null' is not defined
            if action == tool_response.function.name:
                return BotOutput(response=action_input["content"], thought=thought)
            else:
                return BotOutput(action=action, action_input=action_input, thought=thought)
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {llm_response}\n[Result] {result}")
