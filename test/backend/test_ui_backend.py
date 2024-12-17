""" 
align with `src/flowagent/ui_conv/page_single_workflow.py`

USAGE::
    # 1. run the backend firsy
    uvicorn main:app --host 0.0.0.0 --port 8100 --reload
    # 2. test
    python test_ui_backend.py

@241209
- [x] test UI backend logic with CLI. 
@241210
- [x] standardize the conversation logic (with FrontendClient)
"""
import datetime
from flowagent.data import Config, DataManager, LogUtils
from backend import FrontendClient

conversation_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))

client = FrontendClient(cfg)
def main():
    # 1. init the conversation
    conv = client.single_register(conversation_id, cfg)
    while True:
        user_input = LogUtils.format_user_input("[USER] ")
        if user_input == "END": 
            client.single_disconnect(conversation_id)
            break
        client.single_user_input(conversation_id, user_input)

        for i in range(3):
            # 1.0. pre_control
            # 1.1. bot predict. (stream). Stream out the bot's response, and get the final bot_output. 
            stream = client.single_bot_predict(conversation_id)
            for chunk in stream: print(chunk, end="")
            print()
            res_bot_predict = client.single_bot_predict_output(conversation_id)
            bot_output = res_bot_predict.bot_output
            print(f"> bot_output: {bot_output}")
            if bot_output.action:
                # 2. tool
                # 2.0. post_control. Request the action and show the result
                print(LogUtils.format_str_with_color(f"[BOT] {res_bot_predict.msg}", "orange"))
                res_post_control = client.single_post_control(conversation_id, bot_output)
                if not res_post_control.success:
                    print(LogUtils.format_str_with_color(f"[controller error] {res_post_control.msg}", "red"))
                    continue
                # 2.1 (entity linking). TODO: seperate EL from RequestTool
                # 2.2. Get the API response and show
                res_tool = client.single_tool(conversation_id, bot_output)
                print(LogUtils.format_str_with_color(f"[API] {res_tool.msg}", "green"))
            elif bot_output.response:
                # 3. response. Show the response
                print(LogUtils.format_str_with_color(f"[BOT] {bot_output.response}", "orange"))
                break
            else: raise NotImplementedError
        else: print(f"  Failed to get response after 3 attempts!")
    print()

if __name__ == '__main__':
    main()