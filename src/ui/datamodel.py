import yaml
import streamlit as st
from dataclasses import dataclass, asdict

from .bots import PDL_UIBot
from engine_v1.common import DataManager, init_client, LLM_CFG, DIR_data, DIR_ui_log
from engine_v1.apis import BaseAPIHandler, ManualAPIHandler, LLMAPIHandler, VanillaCallingAPIHandler
from engine_v1.datamodel import (
    ConversationHeaderInfos, BaseLogger, Logger, Conversation, ConversationInfos, ActionType
)

def refresh_conversation():
    st.session_state.conversation = Conversation()
    st.session_state.conversation_infos = ConversationInfos.from_components(
        previous_action_type=ActionType.START, num_user_query=0
    )

def refresh_all():
    print(f"[INFO] Refresh all! Current config: {st.session_state.config}")
    refresh_conversation()
    assert 'config' in st.session_state
    init_bot()

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

@dataclass
class Config:
    # workflow_name: str
    model_name: str = "qwen2_72B"
    workflow_dir: str = DIR_data
    template_fn: str = "query_PDL.jinja"
    
    @classmethod
    def from_yaml(cls, yaml_file: str):
        # DONE: read config file
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        return cls(**data)

@st.cache_data
def get_workflow_name_list(workflow_dir:str=DIR_data):
    return DataManager.get_workflow_name_list(workflow_dir)

def init_bot():
    # TODO: implement new Bot!      TODO: only reload pdl file!! 
    assert 'config' in st.session_state
    cfg = st.session_state.config
    st.session_state.bot = PDL_UIBot(st.session_state.client, st.session_state.api_handler, logger=BaseLogger(), template_fn=cfg.template_fn)
    pdl_fn = f"{cfg.workflow_dir}/{st.session_state.workflow_name}.txt"
    st.session_state.bot._load_pdl(pdl_fn)

def init(cfg:Config):
    """ 集中初始化: 替代 CLIInterface.__init__() 
    config: Config
    infos: ConversationHeaderInfos
    client: OpenAIClient
    api_handler: BaseAPIHandler
    """
    assert "workflow_name" in st.session_state, "workflow_name must be selected! "
    # if "workflow_name" not in st.session_state:
    #     st.session_state.workflow_name = cfg.workflow_name
    if "config" not in st.session_state:
        st.session_state.config = cfg
    if "infos" not in st.session_state:
        st.session_state.infos = ConversationHeaderInfos.from_components(st.session_state.workflow_name, cfg.model_name)
    if "logger" not in st.session_state:
        st.session_state.logger = Logger(log_dir=DIR_ui_log)

    if "client" not in st.session_state:
        st.session_state.client = init_client(llm_cfg=LLM_CFG[cfg.model_name])
        st.session_state.api_handler = LLMAPIHandler(st.session_state.client)
        init_bot()