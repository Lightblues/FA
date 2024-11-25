from loguru._logger import Logger
import streamlit as st; self = st.session_state
import json
from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .ui_multi import init_sidebar
from .ui_data import refresh_workflow
from .page_single_workflow import show_conversations

def step_user_input(OBJECTIVE: str):
    conv: Conversation = self.conv
    msg_user = Message(Role.USER, OBJECTIVE, conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id)
    conv.add_message(msg_user)
    with st.chat_message("user", avatar=self['avatars']['user']):
        st.write(OBJECTIVE)
    # self.logger.info(f"{msg_user.to_str()}")

def main_multi():
    """Main loop! see [~ui_conv.md]"""
    if "logger" not in self:
        self.logger = init_loguru_logger(DataManager.DIR_ui_log)
    
    init_sidebar()
    # init_single_workflow()    # TODO: init status
    
    config: Config = self.cfg
    conversation: Conversation = self.conv
    logger: Logger = st.session_state.logger
    
    show_conversations(conversation)
    if OBJECTIVE := st.chat_input('Input...'):
        step_user_input(OBJECTIVE)
