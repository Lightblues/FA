""" 
@241121
- 针对streamlit的形式, 实现了refresh机制: `refresh_config` of workflow, bot, api;  `refresh_pdl` of controller
"""

from typing import List, Dict
import yaml, os, pdb, datetime
import streamlit as st; self = st.session_state

from .uid import get_identity
from .ui_bot import PDL_UIBot
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
    if 'avatars' not in self:
        self['avatars'] = {
            # 'ian': bot_icon,
            'system': '⚙️', # 🖥️
            'user': '💬',   # 🧑‍💻 👤 🙂 🙋‍♂️ / 🙋‍♀️
            'assistant': '🤖',
            'bot': '🤖',
        }
    if 'tool_emoji' not in self:
        self['tool_emoji'] = {
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

    if "headers" not in self:
        headers = st.context.headers
        user_identity = get_identity(headers, app_id="MAWYUI3UXKRDVJBLWMQNGUBDRE5SZOBL")
        # print(f"user_identity: {user_identity}")
        self.headers = headers
        self.user_identity = user_identity

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
    """Init or refresh the conversation"""
    print(f">> Refreshing conversation!")
    if "conv" not in self:
        self.conv = Conversation()
    else:
        self.conv.clear()
        self.conv.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    selected_workflow_name = self.selected_workflow_name.split("-")[-1]
    msg_hello = Message(
        Role.BOT, self.cfg.ui_greeting_msg.format(name=selected_workflow_name), 
        conversation_id=self.conv.conversation_id, utterance_id=self.conv.current_utterance_id)
    self.conv.add_message(msg_hello)
    return self.conv

def refresh_bot() -> PDL_UIBot:
    print(f">> Refreshing bot: `{self.selected_template_fn}` with model `{self.selected_model_name}`")
    cfg:Config = self.cfg
    cfg.bot_template_fn = f"flowagent/{self.selected_template_fn}"
    cfg.bot_llm_name = self.selected_model_name
    if self.user_additional_constraints is not None:
        cfg.ui_user_additional_constraints = self.user_additional_constraints
    
    conv = refresh_conversation()
    if 'bot' not in self:
        self.bot = PDL_UIBot(cfg=cfg, conv=conv, workflow=self.workflow)
        self.api_handler = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=conv, workflow=self.workflow)
    else:
        self.bot.refresh_config(cfg)
        self.api_handler.refresh_config(cfg)
    refresh_controllers()
    return self.bot

def refresh_workflow():
    """refresh workflow -> bot """
    print(f">> Refreshing workflow: `{self.selected_workflow_name}` of ``")
    _, name_id_map = get_workflow_names_map()
    self.cfg.pdl_version = self.selected_pdl_version
    self.cfg.workflow_id = name_id_map['PDL_zh'][self.selected_workflow_name]
    self.workflow.refresh_config(self.cfg)
    refresh_bot()

def refresh_controllers():
    if 'controllers' not in self:
        self.controllers = {}  # {name: BaseController}
        for c in self.cfg.bot_pdl_controllers:
            self.controllers[c['name']] = CONTROLLER_NAME2CLASS[c['name']](self.cfg, self.conv, self.workflow.pdl, c['config'])
    for c in self.controllers.values():
        # NOTE: 仅在更新了pdl的时候,才刷新
        if self.workflow.pdl is not c.pdl:
            c.refresh_pdl(self.workflow.pdl)
