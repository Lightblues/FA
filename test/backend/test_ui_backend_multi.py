"""
align with `ui_conv/page_single_workflow.py`

USAGE::
    # 1. run the backend firsy
    uvicorn main:app --host 0.0.0.0 --port 8100 --reload
    # 2. test
    python test_ui_backend_multi.py

@241209
- [x] test UI backend logic with CLI.
@241210
- [x] standardize the conversation logic (with FrontendClient)

Client
    .multi_register(conversation_id, cfg)
    .multi_disconnect(conversation_id)
    .multi_user_input(conversation_id, user_input)

    .multi_bot_main_predict(conversation_id)
    .multi_bot_main_predict_output(conversation_id)
    .multi_tool_main(conversation_id, agent_main_output)
    .multi_bot_workflow_predict(conversation_id)
    .multi_bot_workflow_predict_output(conversation_id)
    .multi_post_control(conversation_id, bot_output)
    .multi_tool_workflow(conversation_id, bot_output)
"""

from fa_demo.backend import FrontendClient
from fa_core.common import Config, LogUtils, get_session_id


cfg = Config.from_yaml("default.yaml")
client = FrontendClient(cfg.backend_url)
conversation_id = get_session_id()


def step_tool(agent_main_output):
    res_tool = client.multi_tool_main(conversation_id, agent_main_output)
    print(LogUtils.format_str_with_color(f"{res_tool.msg}", "green"))
    return res_tool


def case_main():
    for r in range(3):
        stream = client.multi_bot_main_predict(conversation_id)
        for chunk in stream:
            print(chunk, end="")
        print()
        res_bot_predict = client.multi_bot_main_predict_output(conversation_id)
        agent_main_output = res_bot_predict.bot_output
        if agent_main_output.workflow:
            print(LogUtils.format_str_with_color(f"{res_bot_predict.msg}", "orange"))
            break
        else:
            if agent_main_output.action:
                print(LogUtils.format_str_with_color(f"{res_bot_predict.msg}", "orange"))
                tool_output = step_tool(agent_main_output)
            elif agent_main_output.response:
                print(LogUtils.format_str_with_color(f"{res_bot_predict.msg}", "orange"))
                break
    else:
        print(f"  Failed to get response after 3 attempts!")
    if agent_main_output.workflow:
        case_workflow()


def case_workflow():
    for i in range(5):
        # 1.0. pre_control
        # 1.1. bot predict. (stream). Stream out the bot's response, and get the final bot_output.
        stream = client.multi_bot_workflow_predict(conversation_id)
        for chunk in stream:
            print(chunk, end="")
        print()
        res_bot_predict = client.multi_bot_workflow_predict_output(conversation_id)
        bot_output = res_bot_predict.bot_output
        if bot_output.workflow:
            break
        else:
            if bot_output.action:
                # 2.0. post_control. Request the action and show the result
                print(LogUtils.format_str_with_color(f"{res_bot_predict.msg}", "orange"))
                res_post_control = client.multi_post_control(conversation_id, bot_output)
                if not res_post_control.success:
                    print(LogUtils.format_str_with_color(f"{res_post_control.msg}", "red"))
                    continue
                # 2.1 (entity linking). TODO: seperate EL from RequestTool
                # 2.2. Get the API response and show
                res_tool = client.multi_tool_workflow(conversation_id, bot_output)
                print(LogUtils.format_str_with_color(f"{res_tool.msg}", "green"))
            elif bot_output.response:
                # 3. response. Show the response
                print(LogUtils.format_str_with_color(f"{res_bot_predict.msg}", "orange"))
                break
            else:
                raise NotImplementedError
    else:
        print(f"  Failed to get response after 3 attempts!")
    if bot_output.workflow:
        case_main()


def main():
    # 1. init the conversation
    conv = client.multi_register(conversation_id, cfg)
    print(LogUtils.format_str_with_color(f"{conv.get_last_message()}", "orange"))
    while True:
        user_input = LogUtils.format_user_input("[USER] ")
        if user_input == "END":
            client.multi_disconnect(conversation_id)
            break
        client.multi_user_input(conversation_id, user_input)

        if client.curr_status == "main":
            case_main()
        else:
            case_workflow()

    print()


if __name__ == "__main__":
    main()
