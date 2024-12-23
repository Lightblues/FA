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
"""

import json
import re
from typing import Iterator, List, Tuple, Union

from openai.types.chat.chat_completion_chunk import ChoiceDelta

from common import Formater, PromptUtils, init_client, jinja_render
from data import BotOutput, ToolDefinition

from .react_bot import ReactBot


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

    names = ["UISingleBot", "ui_single_bot"]

    last_llm_chat_completions: List[ChoiceDelta] = []
    last_llm_prompt: str = ""  # the prompt for logging
    last_llm_response: str = ""  # the llm response (with tool calls) for logging
    ui_user_additional_constraints: str = ""

    def _post_init(self) -> None:
        self.bot_template_fn = self.cfg.ui_bot_template_fn
        self.bot_llm_name = self.cfg.ui_bot_llm_name
        self.ui_user_additional_constraints = self.cfg.ui_user_additional_constraints
        self.llm = init_client(self.bot_llm_name)

    def _gen_prompt(self) -> str:
        # - [x]: format apis
        state_infos = {
            "Current time": PromptUtils.get_formated_time(),
        }
        data_handler = self.context.data_handler
        # s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."
        state_infos |= self.context.status_for_prompt  # add the status infos from PDL!
        _tool_infos = [tool.model_dump() for tool in data_handler.pdl.tools]
        # _pdl_info = data_handler.pdl.to_str()
        _pdl_info = data_handler.pdl.to_json()  # NOTE: convert to json instead of str!!
        prompt = jinja_render(
            self.bot_template_fn,
            workflow_name=data_handler.pdl.Name,
            PDL=_pdl_info,
            api_infos=_tool_infos,
            conversation=self.context.conv.to_str(),
            user_additional_constraints=self.ui_user_additional_constraints,
            current_state="\n".join(f"{k}: {v}" for k, v in state_infos.items()),
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
        """Parse output with full `Tought, Action, Action Input, Response`."""
        llm_response = "".join(c.content or "" for c in self.last_llm_chat_completions)
        self.last_llm_response = llm_response
        if "```" in llm_response:
            llm_response = Formater.parse_codeblock(llm_response, type="").strip()
        pattern = r"(Thought|Action|Action Input|Response):\s*(.*?)\s*(?=Thought:|Action:|Action Input:|Response:|\Z)"
        matches = re.finditer(pattern, llm_response, re.DOTALL)
        result = {match.group(1): match.group(2).strip() for match in matches}

        # validate result
        try:
            thought = result.get("Thought", "")
            action = action_input = None
            if "Action" in result:  # Action
                action = result["Action"]
                if action:
                    if action.startswith("API_"):
                        action = action[4:]
                    action_input = json.loads(result["Action Input"])  # eval: NameError: name 'null' is not defined
            response = result.get("Response", "")
            return BotOutput(
                action=action,
                action_input=action_input,
                response=response,
                thought=thought,
            )
        except Exception as e:
            raise RuntimeError(f"Parse error: {e}\n[LLM output] {llm_response}\n[Result] {result}")
