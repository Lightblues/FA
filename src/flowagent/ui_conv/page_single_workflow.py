
""" 
> streamlit run run_ui.py --server.port 8501 -- --config=ui_dev.yaml
url: http://agent-pdl.woa.com

cases: https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPIaxl2WshdR0KQkIBZdF?scode=AJEAIQdfAAolrl13UxAcMATAZtAPI&tab=qe4ogl

@240718 implement basic UI for single workflow
- [x] [feat] show Huabu meta information in the sidebar
- [x] [log] add more detailed logs
- [x] [feat] mofigy template/PDL in the web directly!  -- not good
@240723 update V2 UI
- [x] [feat] clearily log and print infos
- [x] add refresh api (refresh_conversation / refresh_workflow)
@241120 merge to master & refresh
- [x] refactor: align with [~master]
- [x] for streamlit, implement refresh mechanism: `refresh_config` of workflow, bot, api;  `refresh_pdl` of controller
@20241127
- [x] align with test data (https://doc.weixin.qq.com/sheet/e3_AEcAggZ1ACcumx7zFjoQGOBubNd0p?scode=AJEAIQdfAAosxBjyslAcMATAZtAPI&tab=0koe96)
- [x] dataset: huabu_1127
- [x] equip EntityLinker! 
@241202
- [x] #feat select workflow_dataset in UI
"""

import time, os, json, glob, openai, yaml, datetime, pdb, copy, sys
from typing import List
from loguru._logger import Logger
import streamlit as st; ss = st.session_state

from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, BotOutputType, APIOutput
)
from ..roles import BaseBot, BaseUser, BaseTool
from .ui_single import init_sidebar, post_sidebar
from .bot_single import PDL_UIBot
from .data_single import refresh_bot, refresh_workflow, db_upsert_session, fake_stream
from ..utils import retry_wrapper

def show_conversations(conversation: Conversation):
    for message in conversation.msgs:
        if (message.role == Role.SYSTEM) or (message.content.startswith("<")):
            continue
        with st.chat_message(message.role.rolename, avatar=ss['avatars'][message.role.rolename]):
            st.write(message.content)

def _post_control(bot_output: BotOutput, ) -> bool:
    """ Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to ss.conv!
    """
    for controller in ss.controllers.values():
        if not controller.if_post_control: continue
        if not controller.post_control(bot_output): return False
    return True

def _pre_control(bot_output: BotOutput) -> None:
    """ Make pre-control on the bot's action
    will change the PDLBot's prompt! 
    """
    # if not (self.cfg.exp_mode == "session" and isinstance(self.bot, PDLBot)):  return
    for controller in ss.controllers.values():
        print(f"> [pre_control] {controller.name}")
        if not controller.if_pre_control: continue
        controller.pre_control(bot_output)

def step_user_input(OBJECTIVE: str):
    conv: Conversation = ss.conv
    msg_user = Message(Role.USER, OBJECTIVE, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id)
    conv.add_message(msg_user)
    with st.chat_message("user", avatar=ss['avatars']['user']):
        st.write(OBJECTIVE)
    # ss.logger.info(f"{msg_user.to_str()}")

@retry_wrapper(retry=3, step_name="step_bot_prediction", log_fn=ss.logger.bind(custom=True).error)
def step_bot_prediction() -> BotOutput:
    bot:PDL_UIBot = ss.bot
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    prompt, stream = bot.process_stream()
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(stream)
    bot_output: BotOutput = bot.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return bot_output

def step_api_process(bot_output: BotOutput) -> APIOutput:
    tool:BaseTool = ss.tool
    api_output: APIOutput = tool.process(bot_output)        # add message! 
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
    for num_bot_actions in range(ss.cfg.bot_action_limit):
        # 0. pre-control
        _pre_control(bot_output)
        # 1. bot predict an action
        bot_output = step_bot_prediction()
        print(f"> bot_output {bot_output}")

        # 2. STOP: break until bot RESPONSE
        if bot_output.action:
            if not _post_control(bot_output):
                ss.logger.warning(ss.conv.get_last_message().to_str())
                st.markdown(f'<p style="color: red;">[controller error] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
                continue
            api_output = step_api_process(bot_output)
        elif bot_output.response:
            # TODO: add `_response_control` in FlowagentConversationManager
            ss.logger.info(ss.conv.get_last_message().to_str())
            break
        else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
    else:
        pass

    # save to db
    db_upsert_session()


def main_single():
    # 1. init
    init_sidebar()      # need cfg

    if "workflow" not in ss: refresh_workflow()
    if ("mode" not in ss) or (ss.mode == "multi"):
        ss.mode = "single"
        refresh_bot()  # will also refresh .conv

    post_sidebar()      # need conv

    # 3. the main loop!
    show_conversations(ss.conv)
    if OBJECTIVE := st.chat_input('Input...'):
        step_user_input(OBJECTIVE)
        with st.container():
            case_workflow()
        # show final bot response to screen
        with st.chat_message("assistant", avatar=ss['avatars']['assistant']):
            # st.write(ss.conv.get_last_message().content)
            st.write_stream(fake_stream(ss.conv.get_last_message().content))
