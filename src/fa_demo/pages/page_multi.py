"""
cases: https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPIaxl2WshdR0KQkIBZdF?scode=AJEAIQdfAAoAaaG6YXAcMATAZtAPI&tab=BB08J2

@241125 implement main agent (step 1)
- [x] #feat main agent
- [x] seperate single and multi workflow logic (refactor)
@241126
- [x] #feat implement workflow agents
- [x] limit # ActionType.SWITCH in single turn (to avoid dead loop)? Maybe not necessary
@241127
- [x] #feat add activated workflow in the sidebar (ui_multi.py)
@241202
- [x] #bug, cannot refresh ss.conv when changing Single/Multi
- [x] #feat refresh main & all workflow agents in [UI]
- [x] #feat select workflow_dataset in [UI]
@241204
- [x] #feat add tools for main agent (Google Search)
- [x] #feat #robust add error handler -> add retry_wrapper for `step_agent_main_prediction`
- [x] #feat #debug add Mocked LLM (model_name="debug")
@241205
- [x] #feat #log save session infos to db
- [x] #feat optimize visualization: modify `stream_generator` & `fake_stream` @ian
- [x] #feat mock tool output
@241211
- [x] #structure refactor from `ui_conv`
- [x] testing (debug): inspect prompt and output -> `page_inspect.py`
@241231
- [x] #feat update page_multi.py

todos
- [ ] #bug, repeatly SWITCH workflow
- [ ] #doc add standard test cases in doc [cases]
- [ ] #tune set LLM parameters
"""

import streamlit as st


ss = st.session_state
import json
from typing import Union

from fa_server import FrontendClient
from fa_server.typings import MultiBotWorkflowPredictResponse, MultiBotMainPredictResponse
from fa_core.common import retry_wrapper, json_line
from fa_core.data import (
    APIOutput,
    BotOutput,
    Conversation,
)

from ..common import StreamlitUtils, fake_stream
from ..ui.data_multi import init_tools, refresh_session_multi
from ..ui.ui_multi import init_sidebar, post_sidebar


st_utils = StreamlitUtils()


def insert_disconnect_js():
    # JavaScript to notify server on page unload
    # ref: https://discuss.streamlit.io/t/detecting-user-exit-browser-tab-closed-session-end/62066
    st.components.v1.html(
        f"""
        <script>
            window.onbeforeunload = function() {{
                fetch('{ss.client.backend_url}/multi_disconnect/{ss.session_id}', {{
                    method: 'POST'
                }});
            }};
        </script>
    """,
        height=0,
    )


def show_conversations(conversation: Conversation):
    for message in conversation.msgs:
        if not (message.role.rolename == "user" or message.role.rolename.startswith("bot")):
            continue
        elif message.content.startswith("<"):
            continue
        with st.chat_message(message.role.rolename, avatar=ss["avatars"][message.role.rolename]):
            st.write(message.content)


def step_user_input(query: str):
    ss.client.multi_user_input(ss.session_id, query)
    with st.chat_message("user", avatar=ss["avatars"]["user"]):
        st.write(query)


@retry_wrapper(
    retry=3,
    step_name="step_agent_workflow_prediction",
    log_fn=ss.logger.bind(custom=True).error,
)
def step_agent_workflow_prediction() -> BotOutput:
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    client: FrontendClient = ss.client
    with st.expander(f"{ss['tool_emoji']['think']} Thinking...", expanded=True):
        llm_response = st.write_stream(client.multi_bot_workflow_predict(ss.session_id))
    res = client.multi_bot_workflow_predict_output(ss.session_id)
    return res.bot_output


@retry_wrapper(
    retry=3,
    step_name="step_agent_main_prediction",
    log_fn=ss.logger.bind(custom=True).error,
)
def step_agent_main_prediction() -> MultiBotMainPredictResponse:
    print(f">> conversation: {json_line(str(ss.conv))}")
    client: FrontendClient = ss.client
    with st.expander(f"{ss['tool_emoji']['think']} Thinking...", expanded=True):
        _ = st.write_stream(client.multi_bot_main_predict(ss.session_id))
    res = client.multi_bot_main_predict_output(ss.session_id)
    return res


def step_api_process(bot_output: BotOutput) -> APIOutput:
    client: FrontendClient = ss.client
    res = client.multi_tool_workflow(ss.session_id, bot_output)
    st_utils.show_api_call(res.api_output)
    return res.api_output


def step_tool(agent_main_output: BotOutput) -> str:
    client: FrontendClient = ss.client
    # see @ian /cq8/ianxxu/chatchat/_TaskPlan/UI/v2.1/IanAGI.py
    tool_name, tool_args = agent_main_output.action, agent_main_output.action_input
    if tool_name in ("web_search"):
        spinner_info = f"Google searching for {tool_args['query']}..."
    elif tool_name in ("hunyuan_search"):
        spinner_info = f"Hunyuan searching for {tool_args['query']}..."
    else:
        raise NotImplementedError

    with st.spinner(f"{ss['tool_emoji'][tool_name]} {spinner_info}"):
        expander_msg = ""
        if tool_name in ("web_search", "hunyuan_search"):
            expander_msg = f"{ss['tool_emoji']['web_logo']} Searching results for '{tool_args['query']}'"
        else:
            raise NotImplementedError
        with st.expander(expander_msg, expanded=True):
            _ = st.write_stream(client.multi_tool_main_stream(ss.session_id, agent_main_output))
        res = client.multi_tool_main_output(ss.session_id)
        return res


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
                    # TODO: add `_response_control` in ConversationManager
                    # ss.logger.info(f"<case_workflow> bot response: {bot_output.response}")
                    break
                else:
                    raise TypeError(f"Unexpected bot output: {bot_output}")
        else:
            ss.logger.warning(f"<case_workflow> bot actions exceed the limit: {ss.cfg.bot_action_limit}")
            pass  # TODO:
    if bot_output.workflow:
        case_main()


def case_main():
    with st.container():
        for num_bot_actions in range(ss.cfg.bot_action_limit):
            res = step_agent_main_prediction()
            if res.bot_output.workflow:
                st_utils.show_switch_workflow(ss.conv.get_last_message())
                break
            else:
                if res.bot_output.action:
                    _ = step_tool(res.bot_output)
                elif res.bot_output.response:
                    break
                else:
                    raise NotImplementedError
        else:
            ss.logger.warning(f"<case_main> bot actions exceed the limit: {ss.cfg.bot_action_limit}")
            pass  # TODO:
    if res.bot_output.workflow:
        case_workflow()


def main_multi():
    # 1. init
    init_tools()
    init_sidebar()  # need cfg

    if "client" not in ss:
        ss.client = FrontendClient(backend_url=ss.cfg.backend_url)
    if ("mode" not in ss) or (ss.mode == "single") or ("session_id" not in ss):
        ss.mode = "multi"
        refresh_session_multi()  # multi_register

    insert_disconnect_js()
    post_sidebar()  # need conv

    # 3. the main loop!
    show_conversations(ss.conv)
    if query := st.chat_input("Input..."):
        step_user_input(query)
        if ss.client.curr_status == "main":
            case_main()
        else:
            case_workflow()
        # show final bot response to screen
        with st.chat_message("assistant", avatar=ss["avatars"]["assistant"]):
            st.write_stream(fake_stream(ss.conv.get_last_message().content))
