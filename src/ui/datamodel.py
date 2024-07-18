import yaml, os, pdb
import streamlit as st
from dataclasses import dataclass, asdict

from .bots import PDL_UIBot
from engine_v1.common import DataManager, init_client, LLM_CFG, DIR_data, DIR_data_base, DIR_ui_log, DIR_templates
from engine_v1.apis import BaseAPIHandler, ManualAPIHandler, LLMAPIHandler, VanillaCallingAPIHandler
from engine_v1.datamodel import (
    ConversationHeaderInfos, BaseLogger, Logger, Conversation, ConversationInfos, ActionType, Message, Role,
    PDL
)


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

# NOTE: deprecated
# @dataclass
# class Config:
#     # workflow_name: str
#     model_name: str = "qwen2_72B"
#     workflow_dir: str = DIR_data
#     template_fn: str = "query_PDL.jinja"
    
#     @classmethod
#     def from_yaml(cls, yaml_file: str):
#         # DONE: read config file
#         with open(yaml_file, 'r') as file:
#             data = yaml.safe_load(file)
#         return cls(**data)


# @st.cache_data
def get_template_name_list(template_dir:str=DIR_templates, prefix:str="query_"):
    return DataManager.get_template_name_list(template_dir, prefix=prefix)
@st.cache_data
def get_model_name_list():
    return list(LLM_CFG.keys())

@st.cache_data
def get_workflow_dir_list():
    workflow_versions = ["huabu_step3", "manual", "huabu_refine01"]
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
        previous_action_type=ActionType.START, num_user_query=0
    )
    workflow_name = st.session_state.workflow_name.split("-")[-1]
    msg_hello = Message(Role.BOT, f"你好，我是{workflow_name}机器人，有什么可以帮您?")
    st.session_state.conversation.add_message(msg_hello)

def refresh_bot():
    print(f">> Refreshing bot: template_fn: {st.session_state.template_fn} with model {st.session_state.model_name}")
    st.session_state.client = init_client(LLM_CFG[st.session_state.model_name])
    st.session_state.bot = PDL_UIBot(st.session_state.client, st.session_state.api_handler, logger=BaseLogger(), template_fn=st.session_state.template_fn)
    st.session_state.bot.set_pdl(st.session_state.pdl)
    refresh_conversation()          # clear the conversation

def refresh_pdl(dir_change=False, PDL_str:str=None):
    # print(f"PDL_str: {PDL_str[-20:] if PDL_str else 'none'}")
    if PDL_str:
        assert (not dir_change), "dir_change must be False when PDL_str is given!"
        print(f">> Refreshing PDL: with customed PDL_str!")
        st.session_state.pdl.load_from_str(PDL_str)
    else:
        if dir_change:      # NOTE: change workflow_name when changing workflow_dir!
            st.session_state.workflow_name = st.session_state.DICT_workflow_info[st.session_state.workflow_dir][0]
        print(f">> Refreshing PDL: {st.session_state.workflow_dir}/{st.session_state.workflow_name}.txt")
        st.session_state.pdl.load_from_file(f"{st.session_state.workflow_dir}/{st.session_state.workflow_name}.txt")
    st.session_state.bot.set_pdl(st.session_state.pdl)
    refresh_conversation()          # clear the conversation
    # print(f"PDL in session: {st.session_state.pdl.PDL_str[-20:]}")


def init_agents():
    """ 集中初始化: 替代 CLIInterface.__init__() 
    config: Config
    infos: ConversationHeaderInfos
    client: OpenAIClient
    api_handler: BaseAPIHandler
    pdl: PDL
    """
    assert "workflow_name" in st.session_state, "workflow_name must be selected! "   # init_sidebar()
    if "infos" not in st.session_state:
        st.session_state.infos = ConversationHeaderInfos.from_components(st.session_state.workflow_name, st.session_state.model_name)
    if "logger" not in st.session_state:
        st.session_state.logger = Logger(log_dir=DIR_ui_log)
    if "pdl" not in st.session_state:
        st.session_state.pdl = PDL()
    if "client" not in st.session_state:
        st.session_state.client = init_client(llm_cfg=LLM_CFG[st.session_state.model_name])
        st.session_state.api_handler = LLMAPIHandler(st.session_state.client)
        refresh_bot()