"""
Usage::

    python -m fa_eval.cli.chat_cli_multi --cfg cli_multi.yaml --backend_url="http://localhost:8101"

@241209
- [x] test UI backend logic with CLI.
@241210
- [x] standardize the conversation logic (with FrontendClient)
@241230
- [x] #feat Finish `ChatCLIMulti` -> then `page_multi.py`
"""

from fa_server.client import FrontendClient
from fa_server.typings import MultiBotWorkflowPredictResponse, MultiBotMainPredictResponse
from fa_core.common import Config, LogUtils, get_session_id, init_loguru_logger
from fa_core.data import BotOutput, Conversation, FADataManager

init_loguru_logger(log_dir=FADataManager.DIR_log / "cli", stdout_level="WARNING")  # NOTE: set stdout_level to WARNING to avoid verbose logs


class ChatCLIMulti(object):
    def __init__(self, cfg: Config, verbose: bool = False) -> Conversation:
        self.cfg = cfg
        self.client = FrontendClient(backend_url=self.cfg.backend_url)
        self.conversation_id = get_session_id()

        self.verbose = verbose

    def run(self):
        conv = self.client.multi_register(self.conversation_id, self.cfg)
        self._print_bot(conv.get_last_message().content)
        while True:
            is_end = self.step_user()
            if is_end:
                break
            if self.client.curr_status == "main":
                self.case_main()
            else:
                self.case_workflow()
        self.client.multi_disconnect(self.conversation_id)
        return conv

    def case_main(self):
        for i_bot_actions in range(self.cfg.bot_action_limit):
            bot_response = self.step_agent_main_predict()
            if bot_response.bot_output.workflow:
                self._print_bot(f"{self.client.conv.get_last_message().content}")
                break
            else:
                if bot_response.bot_output.action:
                    self._print_bot(bot_response.msg.content)
                    self.step_tool(bot_response)
                elif bot_response.bot_output.response:
                    self._print_bot(bot_response.bot_output.response)
                    break
                else:
                    raise NotImplementedError
        if bot_response.bot_output.workflow:
            self.case_workflow()

    def step_agent_main_predict(self) -> MultiBotMainPredictResponse:
        stream = self.client.multi_bot_main_predict(self.conversation_id)
        for chunk in stream:
            if self.verbose:
                print(chunk, end="")
        if self.verbose:
            print()
        res_bot_predict = self.client.multi_bot_main_predict_output(self.conversation_id)
        if self.verbose:
            print(f"> bot_output: {res_bot_predict.bot_output}")
        return res_bot_predict

    def case_workflow(self):
        for i_bot_actions in range(self.cfg.bot_action_limit):
            bot_response = self.step_agent_workflow_predict()
            if bot_response.bot_output.workflow:
                self._print_bot_workflow(f"{self.client.conv.get_last_message().content}")
                break
            else:
                if bot_response.bot_output.action:
                    self._print_bot_workflow(bot_response.msg.content)
                    if not self.step_post_control(bot_response):
                        continue
                    self.step_api_process(bot_response)
                elif bot_response.bot_output.response:
                    self._print_bot_workflow(bot_response.bot_output.response)
                    break
                else:
                    raise NotImplementedError
        else:
            print(f"  Failed to get response after 3 attempts!")
        if bot_response.bot_output.workflow:
            self.case_main()

    def step_user(self) -> bool:
        user_input = self._print_user()
        if user_input == "END":
            return True
        self.client.multi_user_input(self.conversation_id, user_input)
        return False

    def step_agent_workflow_predict(self) -> MultiBotWorkflowPredictResponse:
        stream = self.client.multi_bot_workflow_predict(self.conversation_id)
        for chunk in stream:
            if self.verbose:
                print(chunk, end="")
        if self.verbose:
            print()
        res_bot_predict = self.client.multi_bot_workflow_predict_output(self.conversation_id)
        if self.verbose:
            print(f"> bot_output: {res_bot_predict.bot_output}")
        return res_bot_predict

    def step_post_control(self, bot_response: MultiBotWorkflowPredictResponse) -> bool:
        res_post_control = self.client.multi_post_control(self.conversation_id, bot_response.bot_output)
        if not res_post_control.success:
            self._print_system(f"[controller error] {res_post_control.msg}")
            return False
        return True

    def step_tool(self, bot_response: MultiBotMainPredictResponse):
        stream = self.client.multi_tool_main_stream(self.conversation_id, bot_response.bot_output)
        for chunk in stream:
            pass
        res_tool = self.client.multi_tool_main_output(self.conversation_id)
        self._print_tool(res_tool.msg.content)
        return res_tool

    def step_api_process(self, bot_response: MultiBotWorkflowPredictResponse):
        res_api = self.client.multi_tool_workflow(self.conversation_id, bot_response.bot_output)
        self._print_tool(res_api.api_output)
        return res_api

    def _print_bot(self, msg: str):
        print(LogUtils.format_str_with_color(f"[BOT] {msg}", "orange"))

    def _print_bot_workflow(self, msg: str):
        print(LogUtils.format_str_with_color(f"[BOT_WORKFLOW] {msg}", "white"))

    def _print_user(self) -> str:
        user_input = LogUtils.format_user_input("[USER] ")
        return user_input

    def _print_tool(self, msg: str):
        print(LogUtils.format_str_with_color(f"[API] {msg}", "green"))

    def _print_system(self, msg: str):
        print(LogUtils.format_str_with_color(f"[SYSTEM] {msg}", "red"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, default="cli_multi.yaml")
    parser.add_argument("--backend_url", type=str, default=None, help="backend url")
    parser.add_argument("--exp_version", type=str, default=None, help="exp version, will be used to differentiate different experiments!")
    parser.add_argument("--workflow_dataset", type=str, default=None, help="workflow dataset")
    parser.add_argument("--workflow_id", type=str, default=None, help="workflow id to be used")
    parser.add_argument("--bot_llm_name", type=str, default=None, help="bot llm name")
    parser.add_argument("--bot_template_fn", type=str, default=None, help="bot template fn")
    parser.add_argument("--ui_greeting_msg", type=str, default=None, help="ui greeting msg")

    parser.add_argument("--verbose", action="store_true", help="verbose mode")
    args = parser.parse_args()

    cfg = Config.from_yaml(args.cfg)
    if args.exp_version:
        cfg.exp_version = args.exp_version
    if args.backend_url:
        cfg.backend_url = args.backend_url
    if args.workflow_dataset:
        cfg.workflow_dataset = args.workflow_dataset
    if args.workflow_id:
        cfg.workflow_id = args.workflow_id
    if args.bot_llm_name:
        cfg.bot_llm_name = args.bot_llm_name
    if args.bot_template_fn:
        cfg.bot_template_fn = args.bot_template_fn
    if args.ui_greeting_msg:
        cfg.ui_greeting_msg = args.ui_greeting_msg

    cli = ChatCLIMulti(cfg, args.verbose)
    cli.run()
