from loguru._logger import Logger
import streamlit as st

from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .ui import init_resource, init_sidebar
from .ui_data import init_all

def main_multi():
    if "logger" not in st.session_state:
        st.session_state.logger = init_loguru_logger(DataManager.DIR_ui_log)
        
    config: Config = st.session_state.config
    conversation: Conversation = st.session_state.conversation
    logger: Logger = st.session_state.logger