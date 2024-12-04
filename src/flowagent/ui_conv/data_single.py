from typing import List, Dict
import yaml, os, pdb, datetime, collections, json, pymongo
import streamlit as st; ss = st.session_state
from pymongo.database import Database

from .uid import get_identity
from .bot_single import PDL_UIBot
from ..data import (
    Conversation, Message, Role,
    Config, DataManager, Workflow
)
from ..utils import LLM_CFG
from ..roles import API_NAME2CLASS
from ..pdl_controllers import CONTROLLER_NAME2CLASS, BaseController

def debug_print_infos() -> None:
    print(f"[DEBUG] Conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    print(f"  > cfg: {ss.cfg}")

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
        ss['avatars'] = collections.defaultdict(lambda: "🤖")
        ss['avatars'] |= {
            # 'ian': bot_icon,
            'system': '⚙️', # 🖥️
            'user': '💬',   # 🧑‍💻 👤 🙂 🙋‍♂️ / 🙋‍♀️
            'assistant': '🤖',
            'bot': '🤖',
        }
    if 'tool_emoji' not in ss:
        ss['tool_emoji'] = collections.defaultdict(lambda: "⚙️")
        ss['tool_emoji'] |= {
            "search": "🔍",
            "web_search": "🔍",
            "search_news": "🔍",
            "search_images": "🔍",
            "think": "🤔",
            "web_logo": "🌐",
            "warning": "⚠️",
            "analysis": "💡",
            "success": "✅",
            "doc_logo": "📄",
            "calc_logo": "🧮",
            "code_logo": "💻",
            "code_logo": "python_executor",
            'default_tool': "⚙️"
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
def get_workflow_dirs(workflow_dataset) -> List[str]:
    return DataManager.get_workflow_versions(workflow_dataset)

@st.cache_data
def get_workflow_names_map() -> Dict[str, List[str]]:
    return DataManager.get_workflow_names_map()

# 参考 app.py 中描述的 BUG
# @st.cache_resource
def init_db():
    if "db" not in ss:
        ss.db = pymongo.MongoClient(ss.cfg.db_uri)[ss.cfg.db_name]
        print(f"> db: {ss.db}")

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
    
    cfg:Config = ss.cfg
    cfg.ui_bot_template_fn = f"flowagent/{ss.selected_template_fn}"
    cfg.ui_bot_llm_name = ss.selected_model_name
    
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
    print(f">> Refreshing workflow: `{ss.selected_workflow_dataset}` -> `{ss.selected_pdl_version}` -> `{ss.selected_workflow_name}`")
    _, name_id_map = get_workflow_names_map()
    ss.cfg.workflow_dataset = ss.selected_workflow_dataset
    ss.cfg.pdl_version = ss.selected_pdl_version
    ss.cfg.workflow_id = name_id_map[ss.cfg.workflow_dataset][ss.selected_workflow_name]
    if 'workflow' not in ss:
        ss.workflow = Workflow(ss.cfg)
    else:
        ss.workflow.refresh_config(ss.cfg)
    refresh_bot()

def refresh_controllers():
    if 'controllers' not in ss:
        ss.controllers = {}  # {name: BaseController}
        for c in ss.cfg.bot_pdl_controllers:
            ss.controllers[c['name']] = CONTROLLER_NAME2CLASS[c['name']](ss.conv, ss.workflow.pdl, c['config'])
    for c in ss.controllers.values():
        # NOTE: 仅在更新了pdl的时候,才刷新
        if ss.workflow.pdl is not c.pdl:
            c.refresh_pdl(ss.workflow.pdl)

def db_upsert_session():
    """Upsert conversation to `db.ui_single_sessions`
    Infos: (sessionid, name, mode[single/multi], infos, conversation, version)...
    """
    _session_info = {
        # model_llm_name, template, etc
        "session_id": ss.conv.conversation_id,
        "user": ss.user_identity,
        "mode": ss.mode,            # "single"
        "conversation": ss.conv.to_list(),
        "config": ss.cfg.to_dict(),
    }
    db: Database = ss.db
    db.ui_single_sessions.replace_one(
        {"session_id": ss.conv.conversation_id},
        _session_info,
        upsert=True
    )