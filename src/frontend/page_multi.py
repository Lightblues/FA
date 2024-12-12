""" 
@241211
"""
import streamlit as st; ss = st.session_state
import json, datetime
from typing import Any, Union
from flowagent.data import Conversation, Message, Role, BotOutput, APIOutput, MainBotOutput
from flowagent.utils import retry_wrapper
from .ui.ui_multi import init_sidebar, post_sidebar
from .ui.data_multi import refresh_session_multi, init_tools
from .common import fake_stream, StreamlitUtils
from backend import FrontendClient
st_utils = StreamlitUtils()

def insert_disconnect_js():
    # JavaScript to notify server on page unload
    # ref: https://discuss.streamlit.io/t/detecting-user-exit-browser-tab-closed-session-end/62066
    st.components.v1.html(f"""
        <script>
            window.onbeforeunload = function() {{
                fetch('{ss.client.url}/multi_disconnect/{ss.session_id}', {{
                    method: 'POST'
                }});
            }};
        </script>
    """, height=0)

def show_conversations(conversation: Conversation):
    for message in conversation.msgs:
        if not (message.role.rolename == "user" or message.role.rolename.startswith("bot")): continue
        elif (message.content.startswith("<")): continue
        with st.chat_message(message.role.rolename, avatar=ss['avatars'][message.role.rolename]):
            st.write(message.content)

def step_user_input(query: str):
    ss.client.multi_user_input(ss.session_id, query)
    with st.chat_message("user", avatar=ss['avatars']['user']):
        st.write(query)

@retry_wrapper(retry=3, step_name="step_agent_workflow_prediction", log_fn=ss.logger.bind(custom=True).error)
def step_agent_workflow_prediction() -> BotOutput:
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    client: FrontendClient = ss.client
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(client.multi_bot_workflow_predict(ss.session_id))
    res = client.multi_bot_workflow_predict_output(ss.session_id)
    return res.bot_output

@retry_wrapper(retry=3, step_name="step_agent_main_prediction", log_fn=ss.logger.bind(custom=True).error)
def step_agent_main_prediction() -> Union[MainBotOutput, Message]:
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    client: FrontendClient = ss.client
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(client.multi_bot_main_predict(ss.session_id))
    res = client.multi_bot_main_predict_output(ss.session_id)
    return res.bot_output, res.msg

def step_api_process(bot_output: BotOutput) -> APIOutput:
    client: FrontendClient = ss.client
    res = client.multi_tool_workflow(ss.session_id, bot_output)
    st_utils.show_api_call(res.api_output)
    return res.api_output

def step_tool(agent_main_output: MainBotOutput) -> Any:
    client: FrontendClient = ss.client
    # see @ian /cq8/ianxxu/chatchat/_TaskPlan/UI/v2.1/IanAGI.py 
    tool_name, tool_args = agent_main_output.action, agent_main_output.action_input
    if tool_name in ("web_search"):
        spinner_info = f"Searching for {tool_args['query']}..."
    else: raise NotImplementedError
    with st.spinner(f"{ss['tool_emoji'][tool_name]} {spinner_info}"):
        # execute!
        res = client.multi_tool_main(ss.session_id, agent_main_output)
    if tool_name in ("web_search"):
        with st.expander(f"{ss['tool_emoji']['web_logo']} Searching results for '{tool_args['query']}'", expanded=False):
            st.write(res.tool_output)
    else: raise NotImplementedError
    return res.tool_output


def case_workflow():
    client: FrontendClient = ss.client
    with st.container():
        for num_bot_actions in range(ss.cfg.bot_action_limit):
            # 0. pre-control -> backend
            # 1. bot predict an action. (with retry)
            bot_output = step_agent_workflow_prediction()

            if bot_output.workflow:
                st_utils.show_switch_workflow(ss.conv.get_last_message())
                break
            else:
                if bot_output.action:
                    res_post_control = client.multi_post_control(ss.session_id, bot_output)
                    if not res_post_control.success:
                        st_utils.show_controller_error(res_post_control.msg)
                        # ss.logger.warning(f"<case_workflow> controller error: {res_post_control.msg}")
                        continue
                    _ = step_api_process(bot_output)
                elif bot_output.response:
                    # TODO: add `_response_control` in FlowagentConversationManager
                    # ss.logger.info(f"<case_workflow> bot response: {bot_output.response}")
                    break
                else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
        else:
            ss.logger.warning(f"<case_workflow> bot actions exceed the limit: {ss.cfg.bot_action_limit}")
            pass # TODO: 
    if bot_output.workflow:
        case_main()

def case_main():
    with st.container():
        for num_bot_actions in range(ss.cfg.bot_action_limit):
            bot_output, msg = step_agent_main_prediction()
            if bot_output.workflow:
                st_utils.show_switch_workflow(ss.conv.get_last_message())
                break
            else:
                if bot_output.action:
                    tool_output = step_tool(bot_output)
                elif bot_output.response:
                    break
                else: raise NotImplementedError
        else:
            ss.logger.warning(f"<case_main> bot actions exceed the limit: {ss.cfg.bot_action_limit}")
            pass # TODO: 
    if bot_output.workflow:
        case_workflow()

def main_multi():
    # 1. init
    init_tools()
    init_sidebar()      # need cfg

    if "client" not in ss: ss.client = FrontendClient()
    if ("mode" not in ss) or (ss.mode == "single") or ("session_id" not in ss):
        ss.mode = "multi"
        refresh_session_multi()  # multi_register

    insert_disconnect_js()
    post_sidebar()      # need conv

    # 3. the main loop!
    show_conversations(ss.conv)
    if query := st.chat_input('Input...'):
        step_user_input(query)
        if ss.client.curr_status == "main":
            case_main()
        else:
            case_workflow()
        # show final bot response to screen
        with st.chat_message("assistant", avatar=ss['avatars']['assistant']):
            st.write_stream(fake_stream(ss.conv.get_last_message().content))


