""" 
@241209
test UI backend logic with CLI. 
"""
import datetime
from flowagent.data import Config, DataManager, Conversation, Message, Role, LogUtils
from frontend.frontend_client import FrontendClient

client = FrontendClient()
conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
def main():
    conv = client.single_register(conversation_id, cfg)
    while True:
        user_input = LogUtils.format_user_input("[USER] ")
        if user_input == "END": break
        # conv.add_message(Message(role=Role.USER, content=user_input, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id))

        for i in range(3):
            print("  sent query...")
            stream = client.single_bot_predict(conversation_id, user_input)
            for chunk in stream: print(chunk, end="")
            bot_output = client.single_bot_predict_output(conversation_id)
            print(f"  bot_output: {bot_output}")

            if bot_output.action:
                print(LogUtils.format_str_with_color(f"[BOT] {bot_output.action}({bot_output.action_input})", "orange"))
                api_output = client.single_tool(conversation_id, bot_output)
                print(f"  api_output: {api_output}")
                print(LogUtils.format_str_with_color(f"[API] {api_output.response_data}", "green"))
            elif bot_output.response:
                print(LogUtils.format_str_with_color(f"[BOT] {bot_output.response}", "orange"))
                break
            else: raise NotImplementedError
        else: print(f"  Failed to get response after 3 attempts!")
    print()

if __name__ == '__main__':
    main()