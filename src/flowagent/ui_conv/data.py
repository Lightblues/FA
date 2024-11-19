from typing import List, Dict
import yaml, os, pdb, datetime
import streamlit as st

from .ui_bot import PDL_UIBot
from ..data import (
    Conversation, Message, Role,
    Config, DataManager, 
    FileLogger, Workflow
)
from ..utils import LLM_CFG
from ..roles import API_NAME2CLASS


@st.cache_data
def get_template_name_list():
    return DataManager.get_template_name_list()

@st.cache_data
def get_model_name_list():
    return list(LLM_CFG.keys())

@st.cache_data
def get_workflow_dirs() -> List[str]:
    return DataManager.get_workflow_dirs()

@st.cache_data
def get_workflow_names_map() -> Dict[str, List[str]]:
    return DataManager.get_workflow_names_map()


def refresh_conversation() -> Conversation:
    print(f">> Refreshing conversation!")
    st.session_state.conversation = Conversation()
    selected_workflow_name = st.session_state.selected_workflow_name.split("-")[-1]
    msg_hello = Message(
        Role.BOT, st.session_state.config.ui_greeting_msg.format(name=selected_workflow_name), 
        conversation_id=st.session_state.conversation.conversation_id, 
        utterance_id=st.session_state.conversation.current_utterance_id)
    st.session_state.conversation.add_message(msg_hello)
    
    # NOTE: logger is bind to a single session! 
    now = datetime.datetime.now()
    st.session_state.t = now
    st.session_state.session_id = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    st.session_state.logger = FileLogger(log_dir=st.session_state.data_manager.DIR_ui_log, t=st.session_state.t)  # note to set the log_dir
    return st.session_state.conversation

def refresh_bot() -> PDL_UIBot:
    print(f">> Refreshing bot: `{st.session_state.selected_template_fn}` with model `{st.session_state.selected_model_name}`")
    cfg:Config = st.session_state.config
    cfg.bot_template_fn = st.session_state.selected_template_fn
    cfg.bot_llm_name = st.session_state.selected_model_name
    
    workflow:Workflow = st.session_state.workflow
    conv = refresh_conversation()
    st.session_state.bot = PDL_UIBot(cfg=cfg, conv=conv, workflow=workflow)
    st.session_state.api_handler = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=conv, workflow=workflow)
    return st.session_state.bot

def refresh_workflow():
    # st.session_state.config.workflow_dataset = ...
    _, name_id_map = get_workflow_names_map()
    st.session_state.config.workflow_id = name_id_map[st.session_state.selected_workflow_dir][st.session_state.selected_workflow_name]
    print(f">> Refreshing workflow: `{st.session_state.config.workflow_id}`\n  {name_id_map[st.session_state.selected_workflow_dir]}")
    st.session_state.workflow = Workflow(st.session_state.config)
    refresh_bot()

def init_all():
    assert "selected_workflow_name" in st.session_state, "workflow_name must be selected! "   # init_sidebar()
    if "bot" not in st.session_state:
        refresh_bot()
