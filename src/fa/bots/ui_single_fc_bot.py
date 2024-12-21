import json
from typing import Iterator
from common import jinja_render, PromptUtils
from .ui_single_bot import UISingleBot, BotOutput


class UISingleFCBot(UISingleBot):
    names = ["UISingleFCBot", "ui_single_fc_bot"]

    def process_stream(self) -> Iterator[str]:
        self.last_llm_prompt = self._gen_prompt()
        response = self.llm.chat_completions_create(
            query=self.last_llm_prompt,
            tools=self.tools,  # NOTE: used in `tools` field!
            tool_choice="auto",
            stream=True,
        )
        self.last_llm_chat_completions = []
        return self.llm.stream_generator(response, collected_deltas=self.last_llm_chat_completions)

    def _gen_prompt(self) -> str:
        # - [x]: format apis
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
            # api_infos=self.tools,
            conversation=self.context.conv.to_str(),
            user_additional_constraints=self.ui_user_additional_constraints,
            current_state="\n".join(f"{k}: {v}" for k, v in state_infos.items()),
        )
        return prompt

    def _parse_react_output(self) -> BotOutput:
        """Rewrite `super()._parse_react_output()` to support tools!"""
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
