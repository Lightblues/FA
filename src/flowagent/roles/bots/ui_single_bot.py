"""
@241211
- [x] #feat implement UISingleBot
    modify from `ui_con/bot_single.py`.
    - replace streamlit with class properties
"""

import json
import re
from typing import Iterator, List, Tuple, Union

from loguru import logger
from openai._streaming import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta

from common import Formater, PromptUtils, init_client, jinja_render

from ...data import BotOutput
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

    # llm: OpenAIClient = None
    # bot_template_fn: str = "flowagent/bot_pdl.jinja"
    names = ["UISingleBot", "ui_single_bot"]
    last_llm_chat_completions: List[ChoiceDelta] = []
    last_llm_response: str = ""
    if_fc: bool = False

    def __init__(self, **args):
        super().__init__(**args)
        self.llm = init_client(self.cfg.ui_bot_llm_name)
        self.if_fc = self.cfg.ui_bot_if_fc

    def _gen_prompt(self) -> str:
        # TODO: format apis. 1) remove URL; 2) add preconditions
        state_infos = {
            "Current time": PromptUtils.get_formated_time(),
        }
        # s_current_state = f"Previous action type: {conversation_infos.curr_action_type.actionname}. The number of user queries: {conversation_infos.num_user_query}."
        state_infos |= self.workflow.pdl.status_for_prompt  # add the status infos from PDL!
        prompt = jinja_render(
            self.cfg.ui_bot_template_fn,
            workflow_name=self.workflow.pdl.Name,  #
            PDL=self.workflow.pdl.to_str_wo_api(),  # .to_str()
            api_infos=self.workflow.toolbox,
            conversation=self.conv.to_str(),
            user_additional_constraints=self.cfg.ui_user_additional_constraints,
            current_state="\n".join(f"{k}: {v}" for k, v in state_infos.items()),
        )
        return prompt

    def _get_tool_list(self):
        # TODO: validate tool formats
        tool_list = []
        for tool in self.workflow.toolbox:
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
        return tool_list

    def process_stream(self) -> Tuple[str, Iterator[str]]:
        prompt = self._gen_prompt()
        client = self.llm.client

        params = {
            "messages": [{"role": "user", "content": prompt}],
            "model": self.llm.model_name,
            "temperature": self.llm.temperature,
            "stream": True,
        }
        if self.if_fc:
            params["tools"] = self._get_tool_list()

        response = client.chat.completions.create(**params)
        self.last_llm_chat_completions = []

        def stream_generator(response: Stream[ChatCompletionChunk]) -> Iterator[str]:
            for chunk in response:
                delta = chunk.choices[0].delta
                self.last_llm_chat_completions.append(delta)
                if delta.content:
                    yield delta.content
                elif delta.tool_calls:
                    function = delta.tool_calls[0].function
                    if function.name:
                        yield f"<API>{function.name}</API>"
                    elif function.arguments:
                        yield function.arguments

        return prompt, stream_generator(response)

    def process_LLM_response(self, prompt: str) -> BotOutput:
        if self.if_fc:
            prediction = self._parse_react_output_fc()
        else:
            prediction = self._parse_react_output()

        if prediction.action:
            msg_content = f"<Call API> {prediction.action}({prediction.action_input})"
        elif prediction.response:
            msg_content = prediction.response
        else:
            raise NotImplementedError
        self.conv.add_message(
            msg_content,
            llm_name=self.cfg.ui_bot_llm_name,
            llm_prompt=prompt,
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
        action, action_input, response = None, "", ""
        for delta in self.last_llm_chat_completions:
            if delta.tool_calls:
                function = delta.tool_calls[0].function
                if function.name:
                    action = function.name
                elif function.arguments:
                    action_input += function.arguments
            elif delta.content:
                response += delta.content
        self.last_llm_response = f"{response}"
        if action:
            self.last_llm_response += f"<API>{action}</API>{action_input}"
        logger.info(f"last_llm_response: {self.last_llm_response}")
        if action:
            return BotOutput(
                action=action,
                action_input=json.loads(action_input),
                response=response,
            )
        else:
            assert response, "response is empty"
            return BotOutput(
                response=response,
            )
