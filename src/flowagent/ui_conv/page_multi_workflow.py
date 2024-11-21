from loguru._logger import Logger
import streamlit as st
import json
from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .ui_multi import init_sidebar
from .ui_data import refresh_workflow
from .page_single_workflow import show_conversations

def main_multi():
    """Main loop! see [~ui_conv.md]"""
    if "logger" not in st.session_state:
        st.session_state.logger = init_loguru_logger(DataManager.DIR_ui_log)
    
    init_sidebar()
    # init_single_workflow()    # TODO: init status
    
    config: Config = st.session_state.config
    conversation: Conversation = st.session_state.conversation
    logger: Logger = st.session_state.logger
    
    show_conversations(conversation)
    if OBJECTIVE := st.chat_input('Input...'):
        msg_user = Message(Role.USER, OBJECTIVE, conversation_id=conversation.conversation_id, utterance_id=conversation.current_utterance_id)
        conversation.add_message(msg_user)
        with st.chat_message("user", avatar=st.session_state['avatars']['user']):
            st.write(OBJECTIVE)
        logger.info(f"{msg_user.to_str()}")
        print(f">> conversation: {json.dumps(str(conversation), ensure_ascii=False)}")
        