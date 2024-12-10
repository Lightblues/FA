""" 
align with `src/flowagent/ui_conv/page_single_workflow.py`

USAGE::
    # 1. run the backend firsy
    uvicorn main_ui_backend:app --host 0.0.0.0 --port 8100 --reload
    # 2. test
    python -m test.backend.test_ui_backend

@241209
- [x] test UI backend logic with CLI. 
@241210
- [x] standardize the conversation logic (with FrontendClient)
"""
import datetime
from flowagent.data import Config, DataManager, LogUtils
from backend import FrontendClient

client = FrontendClient()
conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
def main():
    # 1. init the conversation
    conv = client.single_register(conversation_id, cfg)
    while True:
        user_input = LogUtils.format_user_input("[USER] ")
        if user_input == "END": break
        # conv.add_message(Message(role=Role.USER, content=user_input, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id))

        for i in range(3):
            # 1.0. pre_control
            # 1.1. bot predict. (stream). Stream out the bot's response, and get the final bot_output. 
            stream = client.single_bot_predict(conversation_id, user_input)
            for chunk in stream: print(chunk, end="")
            print()
            bot_output = client.single_bot_predict_output(conversation_id)
            print(f"> bot_output: {bot_output}")
            if bot_output.action:
                # 2. tool
                # 2.0. post_control. Request the action and show the result
                post_control_response = client.single_post_control(conversation_id, bot_output)
                if not post_control_response.success:
                    print(LogUtils.format_str_with_color(f"[controller error] {post_control_response.content}", "red"))
                    continue
                # 2.1 (entity linking). TODO: seperate EL from RequestTool
                # 2.2. Get the API response and show
                print(LogUtils.format_str_with_color(f"[BOT] {bot_output.action}({bot_output.action_input})", "orange"))
                api_output = client.single_tool(conversation_id, bot_output)
                print(LogUtils.format_str_with_color(f"[API] {api_output.response_data}", "green"))
            elif bot_output.response:
                # 3. response. Show the response
                print(LogUtils.format_str_with_color(f"[BOT] {bot_output.response}", "orange"))
                break
            else: raise NotImplementedError
        else: print(f"  Failed to get response after 3 attempts!")
    print()

if __name__ == '__main__':
    main()