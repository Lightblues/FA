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
from ..roles import API_NAME2CLASS, USER_NAME2CLASS, BOT_NAME2CLASS


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

def refresh_conversation():
    print(f">> Refreshing conversation!")
    conversation = st.session_state.conversation = Conversation()
    selected_workflow_name = st.session_state.selected_workflow_name.split("-")[-1]
    msg_hello = Message(Role.BOT, st.session_state.config.ui_greeting_msg.format(name=selected_workflow_name), conversation_id=conversation.conversation_id, utterance_id=conversation.current_utterance_id)
    st.session_state.conversation.add_message(msg_hello)
    
    # NOTE: logger is bind to a single session! 
    now = datetime.datetime.now()
    st.session_state.t = now
    st.session_state.session_id = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    st.session_state.logger = FileLogger(log_dir=st.session_state.data_manager.DIR_ui_log, t=st.session_state.t)  # note to set the log_dir

def refresh_bot():
    print(f">> Refreshing bot: template_fn: {st.session_state.selected_template_fn} with model {st.session_state.selected_model_name}")
    cfg:Config = st.session_state.config

    cfg.bot_template_fn = st.session_state.selected_template_fn
    cfg.bot_llm_name = st.session_state.selected_model_name
    
    st.session_state.config = cfg
    st.session_state.bot = PDL_UIBot(cfg=cfg)

def init_bot():
    cfg:Config = st.session_state.config
    conv:Conversation = st.session_state.conversation
    workflow:Workflow = st.session_state.workflow
    st.session_state.bot = PDL_UIBot(cfg=cfg, conv=conv, workflow=workflow)

def refresh_pdl(dir_change=False, PDL_str:str=None):
    """ 刷新PDL, 同时重制对话
    dir_change: check if the dir of PDL has changed
    """
    # if PDL_str:
    #     assert (not dir_change), "dir_change must be False when PDL_str is given!"
    #     print(f">> Refreshing PDL: with customed PDL_str!")
    #     st.session_state.pdl = PDL.load_from_str(PDL_str)
    # else:
    #     if dir_change:      # NOTE: change workflow_name when changing workflow_dir!
    #         st.session_state.workflow_name = st.session_state.DICT_workflow_info[st.session_state.workflow_dir][0]
    #     print(f">> Refreshing PDL: {st.session_state.workflow_dir}/{st.session_state.workflow_name}.yaml")
    #     st.session_state.pdl = PDL.load_from_file(f"{st.session_state.workflow_dir}/{st.session_state.workflow_name}.yaml")
    # st.session_state.pdl_controller = PDLController(st.session_state.pdl)
    # refresh_conversation()          # clear the conversation
    

def refresh_api():
    cfg:Config = st.session_state.config
    conv:Conversation = st.session_state.conversation
    workflow:Workflow = st.session_state.workflow
    st.session_state.api_handler = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=conv, workflow=workflow)


def init():
    assert "selected_workflow_name" in st.session_state, "workflow_name must be selected! "   # init_sidebar()
    if "conversation" not in st.session_state:
        refresh_conversation()
    if "api_handler" not in st.session_state:
        refresh_api()
    if "bot" not in st.session_state:
        init_bot()