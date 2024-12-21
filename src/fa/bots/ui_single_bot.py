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

from openai._streaming import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta

from common import Formater, PromptUtils, init_client, jinja_render
from data import BotOutput

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
    if_fc: bool = False
    tools: list[dict] = []
    ui_user_additional_constraints: str = ""

    def _post_init(self) -> None:
        self.bot_template_fn = self.cfg.ui_bot_template_fn
        self.bot_llm_name = self.cfg.ui_bot_llm_name
        self.ui_user_additional_constraints = self.cfg.ui_user_additional_constraints
        self.llm = init_client(self.bot_llm_name)
        self.if_fc = self.cfg.ui_bot_if_fc
        if self.if_fc:
            self._init_tools()

    def _gen_prompt(self) -> str:
        # TODO: format apis. 1) remove URL; 2) add preconditions
        state_infos = {
            "Current time": PromptUtils.get_formated_time(),
        }
        data_handler = self.context.data_handler
        # s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."
        state_infos |= self.context.status_for_prompt  # add the status infos from PDL!
        prompt = jinja_render(
            self.bot_template_fn,
            workflow_name=data_handler.pdl.Name,
            PDL=data_handler.pdl.to_str(),
            api_infos=self.tools,
            conversation=self.context.conv.to_str(),
            user_additional_constraints=self.ui_user_additional_constraints,
            current_state="\n".join(f"{k}: {v}" for k, v in state_infos.items()),
        )
        return prompt

    def _init_tools(self):
        # TODO: validate tool formats
        tool_list = []
        for tool in self.context.data_handler.toolbox:
            parameters = tool.get("parameters", {})
            fc = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": {"type": "object", "properties": parameters.get("properties", {}), "required": parameters.get("required", [])},
                },
            }
            tool_list.append(fc)
        self.tools = tool_list
        return tool_list

    def process_stream(self) -> Iterator[str]:
        self.last_llm_prompt = self._gen_prompt()
        response = self.llm.chat_completions_create(query=self.last_llm_prompt, tools=self.tools, tool_choice="auto", stream=True)
        self.last_llm_chat_completions = []
        return self.llm.stream_generator(response, collected_deltas=self.last_llm_chat_completions)

    def process_LLM_response(self) -> BotOutput:
        if self.if_fc:
            prediction = self._parse_react_output_fc()
        else:
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
        llm_response = "".join(c.content for c in self.last_llm_chat_completions)
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

    def _parse_react_output_fc(self) -> BotOutput:
        """Parse output with full `Tought, Action, Action Input, Response`."""
        response, action, action_input = self.llm.proces_collected_deltas(self.last_llm_chat_completions)

        # log the response with tool calls
        self.last_llm_response = f"{response}"
        if action:
            self.last_llm_response += f"<API>{action}</API>{action_input}"

        if action:
            return BotOutput(
                action=action,
                action_input=json.loads(action_input),
                response=response,
            )
        else:
            # assert response, "response is empty"  # can also be not empty?
            return BotOutput(
                response=response,
            )
