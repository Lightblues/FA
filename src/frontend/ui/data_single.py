""" Data for single workflow 

- [ ] can also implemented as service/backend

"""

from typing import List, Dict, Iterator
import yaml, os, pdb, datetime, collections, json, pymongo, time
import streamlit as st; ss = st.session_state
from pymongo.database import Database

from ..common.util_uid import get_identity
from flowagent.data import (
    Config, DataManager, Workflow
)
from flowagent.utils import LLM_CFG
from flowagent.pdl_controllers import CONTROLLER_NAME2CLASS, BaseController

def debug_print_infos() -> None:
    print(f"[DEBUG] Conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    # print(f"  > cfg: {ss.cfg}")

def fake_stream(response: str) -> Iterator[str]:
    for chunk in response:
        yield chunk
        time.sleep(0.02)

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

def get_session_id():
    # "%Y-%m-%d %H:%M:%S.%f"
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def refresh_session():
    """ Refresh the config and init new session
    NOTE: will reset a new session!

    Used config:
        ``Workflow``: workflow_type, workflow_id, pdl_version
            mode | exp_mode | user_mode
        ``UISingleBot``: ui_bot_template_fn, bot_llm_name, bot_retry_limit
        ``RequestTool``: api_entity_linking
            ``EntityLinker``: api_entity_linking_llm, api_entity_linking_template
        ``controllers``: bot_pdl_controllers
    """
    # 1. collect the selected config
    _, name_id_map = get_workflow_names_map()
    cfg: Config = ss.cfg
    cfg.workflow_dataset = ss.selected_workflow_dataset
    cfg.workflow_id = name_id_map[ss.cfg.workflow_dataset][ss.selected_workflow_name]
    cfg.pdl_version = ss.selected_pdl_version
    cfg.ui_bot_template_fn = f"flowagent/{ss.selected_template_fn}"
    cfg.ui_bot_llm_name = ss.selected_model_name

    # 2. init session!
    if "session_id" in ss and ss.session_id:
        # NOTE: disconnect the old session!
        ss.client.single_disconnect(ss.session_id)
    ss.session_id = get_session_id()
    ss.conv = ss.client.single_register(ss.session_id, ss.cfg, ss.user_identity)

