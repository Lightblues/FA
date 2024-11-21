from typing import List, Dict
import yaml, os, pdb, datetime
import streamlit as st

from .uid import get_identity
from .ui_bot import PDL_UIBot
from ..data import (
    Conversation, Message, Role,
    Config, DataManager, 
    Workflow
)
from ..utils import LLM_CFG
from ..roles import API_NAME2CLASS

def init_resource():
    st.set_page_config(
        page_title="PDL Agent",
        page_icon="🍊",
        initial_sidebar_state="auto",
        menu_items={
            # 'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "mailto:easonsshi@tencent.com",
            # 'About': "# This is a header. This is an *extremely* cool app!"
        }
    )
    st.title('️🍊 PDL Agent')
    # 设置sidebar默认width
    setting_stype = """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 300px;
        max-width: 1000px;
        width: 500px;
    }
    """
    st.markdown(setting_stype, unsafe_allow_html=True)

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

    if "headers" not in st.session_state:
        headers = st.context.headers
        user_identity = get_identity(headers, app_id="MAWYUI3UXKRDVJBLWMQNGUBDRE5SZOBL")
        # print(f"user_identity: {user_identity}")
        st.session_state.headers = headers
        st.session_state.user_identity = user_identity
        
        now = datetime.datetime.now()
        st.session_state.t = now
        st.session_state.session_id = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

@st.cache_data
def get_template_name_list():
    return DataManager.get_template_name_list()

@st.cache_data
def get_model_name_list():
    return list(LLM_CFG.keys())

@st.cache_data
def get_workflow_dirs() -> List[str]:
    return DataManager.get_workflow_versions()

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
    return st.session_state.conversation

def refresh_bot() -> PDL_UIBot:
    print(f">> Refreshing bot: `{st.session_state.selected_template_fn}` with model `{st.session_state.selected_model_name}`")
    cfg:Config = st.session_state.config
    cfg.ui_bot_template_fn = f"flowagent/{st.session_state.selected_template_fn}"
    cfg.bot_llm_name = st.session_state.selected_model_name
    if st.session_state.user_additional_constraints is not None:
        cfg.ui_user_additional_constraints = st.session_state.user_additional_constraints
    
    workflow:Workflow = st.session_state.workflow
    conv = refresh_conversation()
    st.session_state.bot = PDL_UIBot(cfg=cfg, conv=conv, workflow=workflow)
    st.session_state.api_handler = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=conv, workflow=workflow)
    return st.session_state.bot

def refresh_workflow():
    """refresh workflow -> bot """
    st.session_state.config.bot_pdl_version = st.session_state.selected_workflow_version
    _, name_id_map = get_workflow_names_map()
    st.session_state.config.workflow_id = name_id_map['PDL_zh'][st.session_state.selected_workflow_name]
    print(f">> Refreshing workflow: `{st.session_state.selected_workflow_name}` of ``")
    st.session_state.workflow = Workflow(st.session_state.config)
    refresh_bot()


