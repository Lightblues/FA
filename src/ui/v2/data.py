import yaml, os, pdb
import streamlit as st

from .bot import PDL_UIBot
from engine_v2 import (
    BaseLogger, Logger, Conversation, ConversationInfos, ConversationHeaderInfos, ActionType, Message, Role,
    PDLController, Config, V01APIHandler, PDL, 
    init_client, LLM_CFG, DataManager, _DIRECTORY_MANAGER
)
# from engine_v1.common import DIR_data, DIR_data_base, DIR_ui_log, DIR_templates, HUABU_versions


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
def get_template_name_list(template_dir:str=_DIRECTORY_MANAGER.DIR_templates, prefix:str="query_"):
    return DataManager.get_template_name_list(template_dir, prefix=prefix)
@st.cache_data
def get_model_name_list():
    return list(LLM_CFG.keys())

@st.cache_data
def get_workflow_dir_list(pdl_version):
    if pdl_version == "v1":
        workflow_versions = _DIRECTORY_MANAGER.HUABU_versions
    elif pdl_version == "v2":
        workflow_versions = _DIRECTORY_MANAGER.HUABU_versions_pdl2
    else:
        raise ValueError(f"Invalid pdl_version: {pdl_version}")
    return [f"{_DIRECTORY_MANAGER.DIR_data_base}/{v}" for v in workflow_versions]
@st.cache_data
def get_workflow_name_list(workflow_dir:str=_DIRECTORY_MANAGER.DIR_huabu_step3, extension:str=".yaml"):
    return DataManager.get_workflow_name_list(workflow_dir, extension=extension)
@st.cache_data
def get_workflow_info_dict(cfg:Config):
    workflow_info_dict = {}
    LIST_workflow_dirs = get_workflow_dir_list(cfg.pdl_version)
    for d in LIST_workflow_dirs:
        workflow_info_dict[d] = get_workflow_name_list(d, cfg.pdl_extension)
    return LIST_workflow_dirs, workflow_info_dict

def refresh_conversation():
    st.session_state.conversation = Conversation()
    st.session_state.conversation_infos = ConversationInfos.from_components(
        curr_role=Role.BOT, curr_action_type=ActionType.START, num_user_query=0
    )
    workflow_name = st.session_state.workflow_name.split("-")[-1]
    msg_hello = Message(Role.BOT, st.session_state.config.greeting_msg.format(name=workflow_name))
    st.session_state.conversation.add_message(msg_hello)
    # NOTE: logger is bind to a single session! 
    st.session_state.logger = Logger(log_dir=_DIRECTORY_MANAGER.DIR_ui_v2_log)  # note to set the log_dir

def refresh_bot():
    print(f">> Refreshing bot: template_fn: {st.session_state.template_fn} with model {st.session_state.model_name}")
    _config:Config = st.session_state.config
    _config.template_fn = st.session_state.template_fn
    _config.model_name = st.session_state.model_name
    _config.normalize_paths()
    
    st.session_state.config = _config
    st.session_state.bot = PDL_UIBot(cfg=_config)
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


def init(config_version:str="default.yaml"):
    """ 集中初始化: 替代 CLIInterface.__init__() 
    config: Config
    infos: ConversationHeaderInfos
    api_handler: BaseAPIHandler
    pdl: PDL
    """
    assert "workflow_name" in st.session_state, "workflow_name must be selected! "   # init_sidebar()
    if "api_handler" not in st.session_state:
        st.session_state.api_handler = V01APIHandler()
        refresh_bot()