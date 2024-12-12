""" 

@241209 
- [x] basic UI implement from [ui_conv] -> Front-Backend Separation
    -> see `backend/client.py`
@241211
- [x] #log move logger to backend
- [x] #feat UI align with `src/flowagent/ui_conv/page_single_workflow.py`
    logic align with `test/backend/test_ui_backend.py`
- [x] #feat refresh sessionId when session is changed; 
    check the time to `refresh_session()`!
- [x] submit `single_disconnect` to clear backend cache (with `single_register`)
- [x] #feat add `single_disconnect` to clear the session context when user exit the page

todos
- [ ] #bug check the controllers
"""
import streamlit as st; ss = st.session_state
import json, datetime
from flowagent.data import Conversation, Message, Role, BotOutput, APIOutput
from flowagent.utils import retry_wrapper
from .ui.ui_single import init_sidebar, post_sidebar
from .ui.data_single import refresh_session_single
from .common import fake_stream, StreamlitUtils
from backend import FrontendClient
st_utils = StreamlitUtils()

def insert_disconnect_js():
    # JavaScript to notify server on page unload
    # ref: https://discuss.streamlit.io/t/detecting-user-exit-browser-tab-closed-session-end/62066
    st.components.v1.html(f"""
        <script>
            window.onbeforeunload = function() {{
                fetch('{ss.client.url}/single_disconnect/{ss.session_id}', {{
                    method: 'POST'
                }});
            }};
        </script>
    """, height=0)

def show_conversations(conversation: Conversation):
    for message in conversation.msgs:
        if (message.role == Role.SYSTEM) or (message.content.startswith("<")):
            continue
        with st.chat_message(message.role.rolename, avatar=ss['avatars'][message.role.rolename]):
            st.write(message.content)

def step_user_input(query: str):
    ss.client.single_user_input(ss.session_id, query)
    with st.chat_message("user", avatar=ss['avatars']['user']):
        st.write(query)

@retry_wrapper(retry=3, step_name="step_bot_prediction", log_fn=ss.logger.bind(custom=True).error)
def step_bot_prediction() -> BotOutput:
    """Get the bot's output (with previos user query of tool output, so there is no need to pass the query).

    Returns:
        BotOutput: the bot's output
    """
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    client: FrontendClient = ss.client
    
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(client.single_bot_predict(ss.session_id))
    res = client.single_bot_predict_output(ss.session_id)
    return res.bot_output

def step_api_process(bot_output: BotOutput) -> APIOutput:
    client: FrontendClient = ss.client
    res = client.single_tool(ss.session_id, bot_output)
    st_utils.show_api_call(res.api_output)
    return res

def case_workflow():
    """ 
    add to db
    1. session level: (sessionid, name, mode[single/multi], infos, conversation, version)
    2. turn level (optional?): (sessionid, turnid, bot_output, prompt, version) TODO:
    """
    client: FrontendClient = ss.client
    with st.container():
        for num_bot_actions in range(ss.cfg.bot_action_limit):
            # 0. pre-control -> backend
            # 1. bot predict an action. (with retry)
            bot_output = step_bot_prediction()

            # 2. STOP: break until bot RESPONSE
            if bot_output.action:
                res_post_control = client.single_post_control(ss.session_id, bot_output)
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
            st.logger.warning(f"<case_workflow> bot actions exceed the limit: {ss.cfg.bot_action_limit}")
            pass # TODO: 


def main_single():
    # 1. init
    init_sidebar()      # need cfg

    if "client" not in ss: ss.client = FrontendClient()
    if ("mode" not in ss) or (ss.mode == "multi") or ("session_id" not in ss):
        ss.mode = "single"
        refresh_session_single()  # single_register

    insert_disconnect_js()
    post_sidebar()      # need conv

    # 3. the main loop!
    show_conversations(ss.conv)
    if query := st.chat_input('Input...'):
        step_user_input(query)
        case_workflow()
        # show final bot response to screen
        with st.chat_message("assistant", avatar=ss['avatars']['assistant']):
            st.write_stream(fake_stream(ss.conv.get_last_message().content))

