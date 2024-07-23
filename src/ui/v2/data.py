import yaml, os, pdb
import streamlit as st
from dataclasses import dataclass, asdict

from .bot import PDL_UIBot
from engine_v2 import (
    BaseLogger, Logger, Conversation, ConversationInfos, ConversationHeaderInfos, ActionType, Message, Role,
    PDLController, Config, V01APIHandler, PDL, 
    init_client, LLM_CFG, DataManager
)
from engine_v1.common import DIR_data, DIR_data_base, DIR_ui_log, DIR_templates, HUABU_versions


def init_resource():
    # bot_icon = Image.open('resource/icon.png')
    if 'avatars' not in st.session_state:
        st.session_state['avatars'] = {
            # 'ian': bot_icon,
            'system': '⚙️', # 🖥️
            'user': '💬',   # 🧑‍💻 👤 🙂 🙋‍♂️ / 🙋‍♀️
            'assistant': '🤖',
            'bot': '🤖',
        }
    if 'tool_emoji' not in st.session_state:
        st.session_state['tool_emoji'] = {
            "search": "🔍",
            "think": "🤔",
            "web_logo": "🌐",
            "warning": "⚠️",
            "analysis": "💡",
            "success": "✅",
            "doc_logo": "📄",
            "calc_logo": "🧮",
            "code_logo": "💻",
        }

# @st.cache_data
def get_template_name_list(template_dir:str=DIR_templates, prefix:str="query_"):
    return DataManager.get_template_name_list(template_dir, prefix=prefix)
@st.cache_data
def get_model_name_list():
    return list(LLM_CFG.keys())

@st.cache_data
def get_workflow_dir_list():
    workflow_versions = HUABU_versions
    return [f"{DIR_data_base}/{v}" for v in workflow_versions]
@st.cache_data
def get_workflow_name_list(workflow_dir:str=DIR_data):
    return DataManager.get_workflow_name_list(workflow_dir)
@st.cache_data
def get_workflow_info_dict():
    workflow_info_dict = {}
    LIST_workflow_dirs = get_workflow_dir_list()
    for d in LIST_workflow_dirs:
        workflow_info_dict[d] = get_workflow_name_list(d)
    return LIST_workflow_dirs, workflow_info_dict

def refresh_conversation():
    st.session_state.conversation = Conversation()
    st.session_state.conversation_infos = ConversationInfos.from_components(
        previous_action_type=ActionType.USER, num_user_query=0
    )
    workflow_name = st.session_state.workflow_name.split("-")[-1]
    msg_hello = Message(Role.BOT, f"你好，我是{workflow_name}机器人，有什么可以帮您?")
    st.session_state.conversation.add_message(msg_hello)

def refresh_bot():
    print(f">> Refreshing bot: template_fn: {st.session_state.template_fn} with model {st.session_state.model_name}")
    _config:Config = st.session_state.config
    _config.template_fn = st.session_state.template_fn
    _config.model_name = st.session_state.model_name
    _config.normalize_paths()
    
    st.session_state.config = _config
    st.session_state.bot = PDL_UIBot(cfg=_config)
    # st.session_state.bot = PDL_UIBot(st.session_state.client, st.session_state.api_handler, logger=BaseLogger(), template_fn=st.session_state.template_fn)
    refresh_conversation()          # clear the conversation

def refresh_pdl(dir_change=False, PDL_str:str=None):
    if PDL_str:
        assert (not dir_change), "dir_change must be False when PDL_str is given!"
        print(f">> Refreshing PDL: with customed PDL_str!")
        st.session_state.pdl = PDL.load_from_str(PDL_str)
    else:
        if dir_change:      # NOTE: change workflow_name when changing workflow_dir!
            st.session_state.workflow_name = st.session_state.DICT_workflow_info[st.session_state.workflow_dir][0]
        print(f">> Refreshing PDL: {st.session_state.workflow_dir}/{st.session_state.workflow_name}.txt")
        st.session_state.pdl = PDL.load_from_file(f"{st.session_state.workflow_dir}/{st.session_state.workflow_name}.txt")
    st.session_state.pdl_controller = PDLController(st.session_state.pdl)
    refresh_conversation()          # clear the conversation


def init_agents():
    """ 集中初始化: 替代 CLIInterface.__init__() 
    config: Config
    infos: ConversationHeaderInfos
    api_handler: BaseAPIHandler
    pdl: PDL
    """
    assert "workflow_name" in st.session_state, "workflow_name must be selected! "   # init_sidebar()
    if "config" not in st.session_state:
        st.session_state.config = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    if "logger" not in st.session_state:
        st.session_state.logger = Logger(log_dir=DIR_ui_log)
    if "bot" not in st.session_state:
        st.session_state.api_handler = V01APIHandler()
        refresh_bot()