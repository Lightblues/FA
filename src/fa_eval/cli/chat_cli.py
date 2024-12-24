"""
Usage::

    python -m fa_eval.cli.chat_cli --cfg dev.yaml
"""

from fa_demo.backend import FrontendClient, SingleBotPredictResponse
from fa_core.common import Config, LogUtils, get_session_id
from fa_core.data import BotOutput


class ChatCLI(object):
    def __init__(self, cfg_name: str, backend_url: str = None):
        self.cfg = Config.from_yaml(cfg_name)
        self.client = FrontendClient(backend_url or self.cfg.backend_url)
        self.conversation_id = get_session_id()

    def run(self):
        self.client.single_register(self.conversation_id, self.cfg)
        while True:
            is_end = self.step_user()
            if is_end:
                break

            for i_bot_actions in range(self.cfg.bot_action_limit):
                bot_response = self.step_bot_predict()
                if bot_response.bot_output.action:
                    print(LogUtils.format_str_with_color(f"[BOT] {bot_response.msg}", "orange"))
                    if not self.step_post_control(bot_response):
                        continue
                    self.step_tool(bot_response)
                elif bot_response.bot_output.response:
                    print(LogUtils.format_str_with_color(f"[BOT] {bot_response.bot_output.response}", "orange"))
                    break
                else:
                    raise NotImplementedError
            else:
                print(f"  Failed to get response after 3 attempts!")
        self.client.single_disconnect(self.conversation_id)

    def step_user(self) -> bool:
        user_input = LogUtils.format_user_input("[USER] ")
        if user_input == "END":
            self.client.single_disconnect(self.conversation_id)
            return True
        self.client.single_user_input(self.conversation_id, user_input)
        return False

    def step_bot_predict(self) -> SingleBotPredictResponse:
        stream = self.client.single_bot_predict(self.conversation_id)
        for chunk in stream:
            print(chunk, end="")
        print()
        res_bot_predict = self.client.single_bot_predict_output(self.conversation_id)
        print(f"> bot_output: {res_bot_predict.bot_output}")
        return res_bot_predict

    def step_post_control(self, bot_response: SingleBotPredictResponse) -> bool:
        # 2.0. post_control. Request the action and show the result
        res_post_control = self.client.single_post_control(self.conversation_id, bot_response.bot_output)
        if not res_post_control.success:
            print(LogUtils.format_str_with_color(f"[controller error] {res_post_control.msg}", "red"))
            return False
        return True

    def step_tool(self, bot_response: SingleBotPredictResponse):
        # 2.1 (entity linking). TODO: seperate EL from RequestTool
        # 2.2. Get the API response and show
        res_tool = self.client.single_tool(self.conversation_id, bot_response.bot_output)
        print(LogUtils.format_str_with_color(f"[API] {res_tool.msg}", "green"))
        return res_tool


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", type=str, default="dev.yaml")
    parser.add_argument("--backend_url", type=str, default="http://localhost:8101")
    args = parser.parse_args()

    cli = ChatCLI(args.cfg, args.backend_url)
    cli.run()
