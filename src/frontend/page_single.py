""" 
@241209 
- [x] basic UI implement from [ui_conv] -> Front-Backend Separation
    - [x] `step_bot_prediction` with `FrontendClient`
    - [ ] `step_api_process`

- [ ] refresh sessionId when session is changed; submit `single_disconnect` to clear backend cache (with `single_register`)
"""
import streamlit as st; ss = st.session_state
import json
from flowagent.data import Conversation, Message, Role, BotOutput, APIOutput
from flowagent.utils import retry_wrapper
from flowagent.ui_conv.ui_single import init_sidebar, post_sidebar
from .util_frontend import fake_stream
from .frontend_client import FrontendClient

def show_conversations(conversation: Conversation):
    for message in conversation.msgs:
        if (message.role == Role.SYSTEM) or (message.content.startswith("<")):
            continue
        with st.chat_message(message.role.rolename, avatar=ss['avatars'][message.role.rolename]):
            st.write(message.content)

def step_user_input(OBJECTIVE: str):
    conv: Conversation = ss.conv
    msg_user = Message(role=Role.USER, content=OBJECTIVE, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id)
    conv.add_message(msg_user)
    with st.chat_message("user", avatar=ss['avatars']['user']):
        st.write(OBJECTIVE)

@retry_wrapper(retry=3, step_name="step_bot_prediction", log_fn=ss.logger.bind(custom=True).error)
def step_bot_prediction() -> BotOutput:
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    client: FrontendClient = ss.client
    
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(client.single_bot_predict(ss.conv.conversation_id, ss.conv))
    bot_output = client.single_bot_predict_output(ss.conv.conversation_id)
    # _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    # ss.logger.bind(custom=True).debug(_debug_msg)
    return bot_output

def step_api_process(bot_output: BotOutput) -> APIOutput:
    client: FrontendClient = ss.client
    api_output = client.single_tool(ss.conv.conversation_id, bot_output)
    st.markdown(f'<p style="color: green;">[API call] Got <code>{api_output.response_data}</code> from <code>{api_output.request}</code></p>', unsafe_allow_html=True)
    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return api_output

def case_workflow():
    """ 
    add to db
    1. session level: (sessionid, name, mode[single/multi], infos, conversation, version)
    2. turn level (optional?): (sessionid, turnid, bot_output, prompt, version) TODO:
    """
    bot_output: BotOutput = None
    # for num_bot_actions in range(ss.cfg.bot_action_limit):
    for num_bot_actions in range(1):
        # 0. pre-control
        # _pre_control(bot_output)
        # 1. bot predict an action
        bot_output = step_bot_prediction()
        print(f"> bot_output {bot_output}")

        # 2. STOP: break until bot RESPONSE
        if bot_output.action:
            # TODO: post_control
            # if not _post_control(bot_output):
            #     ss.logger.warning(ss.conv.get_last_message().to_str())
            #     st.markdown(f'<p style="color: red;">[controller error] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
            #     continue
            api_output = step_api_process(bot_output)
        elif bot_output.response:
            # TODO: add `_response_control` in FlowagentConversationManager
            ss.logger.info(ss.conv.get_last_message().to_str())
            break
        else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
    else:
        pass

def main_single():
    # 1. init
    init_sidebar()      # need cfg

    if "client" not in ss: ss.client = FrontendClient()
    # if "workflow" not in ss: refresh_workflow()
    # if ("mode" not in ss) or (ss.mode == "multi"):
    #     ss.mode = "single"
    #     refresh_bot()  # will also refresh .conv

    # post_sidebar()      # need conv

    # 3. the main loop!
    conversation_id = "xxx"
    ss.conv = ss.client.single_register(conversation_id, ss.cfg)
    show_conversations(ss.conv)
    if OBJECTIVE := st.chat_input('Input...'):
        step_user_input(OBJECTIVE)
        with st.container():
            case_workflow()
        # show final bot response to screen
        with st.chat_message("assistant", avatar=ss['avatars']['assistant']):
            # st.write(ss.conv.get_last_message().content)
            st.write_stream(fake_stream(ss.conv.get_last_message().content))

