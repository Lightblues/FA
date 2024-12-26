from typing import Any, Optional
from pydantic import BaseModel

from fa_demo.backend import FrontendClient, SingleBotPredictResponse
from fa_core.common import Config, LogUtils, get_session_id
from fa_core.data import BotOutput, Conversation
from fa_eval.data import FixedQueries


class FixedQuerySimulator(BaseModel):
    cfg: Config
    fixed_queries: FixedQueries
    verbose: bool = False

    conversation_id: str = ""
    client: Optional[FrontendClient] = None
    conversation: Optional[Conversation] = None

    def model_post_init(self, __context: Any) -> None:
        self.conversation_id = get_session_id()
        self.client = FrontendClient(backend_url=self.cfg.backend_url)
        return super().model_post_init(__context)

    def run(self) -> Conversation:
        conv = self.step_register()
        for query in self.fixed_queries.user_queries:
            self.step_user(query)
            for i_bot_actions in range(self.cfg.bot_action_limit):
                bot_response = self.step_bot_predict()
                if bot_response.bot_output.action:
                    self._print_bot(bot_response.msg)
                    if not self.step_post_control(bot_response):
                        continue
                    self.step_tool(bot_response)
                elif bot_response.bot_output.response:
                    self._print_bot(bot_response.bot_output.response)
                    break
                else:
                    raise NotImplementedError
        self.client.single_disconnect(self.conversation_id)
        return conv

    def step_post_control(self, bot_response: SingleBotPredictResponse) -> bool:
        res_post_control = self.client.single_post_control(self.conversation_id, bot_response.bot_output)
        if not res_post_control.success:
            self._print_system(f"[controller error] {res_post_control.msg}")
            return False
        return True

    def step_tool(self, bot_response: SingleBotPredictResponse):
        res_tool = self.client.single_tool(self.conversation_id, bot_response.bot_output)
        self._print_tool(res_tool.msg)
        return res_tool

    def step_register(self) -> Conversation:
        conv = self.client.single_register(self.conversation_id, self.cfg)
        self._print_bot(conv.get_last_message().content)
        return conv

    def step_user(self, query: str) -> None:
        self.client.single_user_input(self.conversation_id, query)
        self._print_user(query)
        return None

    def step_bot_predict(self) -> SingleBotPredictResponse:
        stream = self.client.single_bot_predict(self.conversation_id)
        for chunk in stream:
            if self.verbose:
                print(chunk, end="")
        if self.verbose:
            print()
        res_bot_predict = self.client.single_bot_predict_output(self.conversation_id)
        if self.verbose:
            print(f"> bot_output: {res_bot_predict.bot_output}")
        return res_bot_predict

    def _print_bot(self, msg: str):
        if self.verbose:
            print(LogUtils.format_str_with_color(f"[BOT] {msg}", "orange"))

    def _print_user(self, msg: str):
        if self.verbose:
            print(LogUtils.format_str_with_color(f"[USER] {msg}", "bold_blue"))

    def _print_tool(self, msg: str):
        if self.verbose:
            print(LogUtils.format_str_with_color(f"[API] {msg}", "green"))

    def _print_system(self, msg: str):
        print(LogUtils.format_str_with_color(f"[SYSTEM] {msg}", "red"))
