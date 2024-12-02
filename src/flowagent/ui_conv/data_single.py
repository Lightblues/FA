""" 
@241121
- 针对streamlit的形式, 实现了refresh机制: `refresh_config` of workflow, bot, api;  `refresh_pdl` of controller
"""

from typing import List, Dict
import yaml, os, pdb, datetime
import streamlit as st; ss = st.session_state

from .uid import get_identity
from .bot_single import PDL_UIBot
from ..data import (
    Conversation, Message, Role,
    Config, DataManager
)
from ..utils import LLM_CFG
from ..roles import API_NAME2CLASS
from ..pdl_controllers import CONTROLLER_NAME2CLASS, BaseController

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
    if 'avatars' not in ss:
        ss['avatars'] = {
            # 'ian': bot_icon,
            'system': '⚙️', # 🖥️
            'user': '💬',   # 🧑‍💻 👤 🙂 🙋‍♂️ / 🙋‍♀️
            'assistant': '🤖',
            'bot': '🤖',
        }
    if 'tool_emoji' not in ss:
        ss['tool_emoji'] = {
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

    if "headers" not in ss:
        headers = st.context.headers
        user_identity = get_identity(headers, app_id="MAWYUI3UXKRDVJBLWMQNGUBDRE5SZOBL")
        # print(f"user_identity: {user_identity}")
        ss.headers = headers
        ss.user_identity = user_identity

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
    """ refresh the conversation (instead of new one) """
    print(f">> Refreshing conversation!")
    if "conv" not in ss: ss.conv = Conversation()
    else:
        ss.conv.clear()
        ss.conv.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    
    selected_workflow_name = ss.selected_workflow_name.split("-")[-1]
    msg_hello = Message(
        Role.BOT, ss.cfg.ui_greeting_msg.format(name=selected_workflow_name), 
        conversation_id=ss.conv.conversation_id, utterance_id=ss.conv.current_utterance_id)
    ss.conv.add_message(msg_hello)
    return ss.conv

def refresh_bot() -> PDL_UIBot:
    """refresh the bot and tool

    Returns:
        PDL_UIBot: bot
    """
    print(f">> Refreshing bot: `{ss.selected_template_fn}` with model `{ss.selected_model_name}`")
    conv = refresh_conversation()
    
    cfg:Config = ss.cfg  # update ss.cfg will also update ss.bot?
    cfg.bot_template_fn = f"flowagent/{ss.selected_template_fn}"
    cfg.bot_llm_name = ss.selected_model_name
    
    if 'bot' not in ss:
        ss.bot = PDL_UIBot()
        ss.tool = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=conv, workflow=ss.workflow)
    else:
        ss.bot.refresh_config()
        ss.tool.refresh_config(cfg)
    refresh_controllers()
    return ss.bot

def refresh_workflow():
    """refresh workflow -> bot """
    print(f">> Refreshing workflow: `{ss.selected_workflow_name}` of ``")
    _, name_id_map = get_workflow_names_map()
    ss.cfg.pdl_version = ss.selected_pdl_version
    ss.cfg.workflow_id = name_id_map['PDL_zh'][ss.selected_workflow_name]
    ss.workflow.refresh_config(ss.cfg)
    refresh_bot()

def refresh_controllers():
    if 'controllers' not in ss:
        ss.controllers = {}  # {name: BaseController}
        for c in ss.cfg.bot_pdl_controllers:
            ss.controllers[c['name']] = CONTROLLER_NAME2CLASS[c['name']](ss.cfg, ss.conv, ss.workflow.pdl, c['config'])
    for c in ss.controllers.values():
        # NOTE: 仅在更新了pdl的时候,才刷新
        if ss.workflow.pdl is not c.pdl:
            c.refresh_pdl(ss.workflow.pdl)
