
""" 
> streamlit run run_ui.py --server.port 8501
url: http://agent-pdl.woa.com

@240718 实现基本交互界面
- [ ] [optimize] optimize API output! 
- [x] [feat] show Huabu meta information in the sidebar
- [x] [log] add more detailed logs
- [x] [feat] mofigy template/PDL in the web directly!  -- not good
@240723 完成V2版本的UI
- [x] [feat] clearily log and print infos

- [x] refactor: align with [~master]
"""

import time, os, json, glob, openai, yaml, datetime, pdb, copy, sys
from typing import List
from loguru._logger import Logger
import streamlit as st; self = st.session_state

from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, BotOutputType, APIOutput
)
from .ui_single import init_sidebar, post_sidebar
from .ui_data import refresh_bot, refresh_conversation

def show_conversations(conversation):
    for message in conversation.msgs:
        if (message.role == Role.SYSTEM) or (message.content.startswith("<")):
            continue  
        with st.chat_message(message.role.rolename, avatar=self['avatars'][message.role.rolename]):
            st.write(message.content)

def _post_control(bot_output: BotOutput, ) -> bool:
    """ Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to self.conv!
    """
    for controller in self.controllers.values():
        if not controller.if_post_control: continue
        if not controller.post_control(bot_output): return False
    return True

def step_user_input(OBJECTIVE: str):
    conv: Conversation = self.conv
    msg_user = Message(Role.USER, OBJECTIVE, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id)
    conv.add_message(msg_user)
    with st.chat_message("user", avatar=self['avatars']['user']):
        st.write(OBJECTIVE)
    # self.logger.info(f"{msg_user.to_str()}")

def step_bot_prediction() -> BotOutput:
    print(f">> conversation: {json.dumps(str(self.conv), ensure_ascii=False)}")
    prompt, stream = self.bot.process_stream()
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(stream)
    bot_output: BotOutput = self.bot.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    self.logger.bind(custom=True).debug(_debug_msg)
    return bot_output

def step_api_process(bot_output: BotOutput) -> APIOutput:
    api_output: APIOutput = self.api_handler.process(bot_output)        # add message! 
    st.markdown(f'<p style="color: green;">[API call] Got <code>{api_output.response_data}</code> from <code>{api_output.request}</code></p>', unsafe_allow_html=True)
    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    self.logger.bind(custom=True).debug(_debug_msg)
    return api_output

def main_single():
    # 1. init
    if "logger" not in self:
        self.logger = init_loguru_logger(DataManager.DIR_ui_log)
    if "workflow" not in self:
        self.workflow = Workflow(self.cfg)
    init_sidebar()      # need cfg

    if "conv" not in self:
        refresh_conversation()
    if "bot" not in self:
        refresh_bot()

    post_sidebar()      # need conv
    
    # 2. prepare for session conversation
    cfg: Config = self.cfg
    conv: Conversation = self.conv
    logger: Logger = self.logger
    # workflow: Workflow = self.workflow

    # 3. the main loop!
    show_conversations(conv)
    if OBJECTIVE := st.chat_input('Input...'):
        step_user_input(OBJECTIVE)
        with st.container():
            num_bot_actions = 0
            while True:
                # 0. pre-control
                # self._pre_control(bot_output)
                # 1. bot predict an action
                bot_output = step_bot_prediction()

                # 2. STOP: break until bot RESPONSE
                if bot_output.action_type == BotOutputType.RESPONSE:
                    logger.info(conv.get_last_message().to_str())
                    break
                elif bot_output.action_type == BotOutputType.ACTION:
                    if not _post_control(bot_output):
                        logger.warning(conv.get_last_message().to_str())
                        st.markdown(f'<p style="color: red;">[controller error] <code>{conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
                        continue
                    # 3.2 call the API (system)
                    api_output = step_api_process(bot_output)
                else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
                
                num_bot_actions += 1
                if num_bot_actions > cfg.bot_action_limit: 
                    break
        # show final bot response to screen
        with st.chat_message("assistant", avatar=self['avatars']['assistant']):
            st.write(conv.get_last_message().content)

        # DB
        # infos_dict = {
        #     "conversation_id": conversation.conversation_id, **config.to_dict()
        # }