""" Data for single workflow 

- [ ] can also implemented as service/backend

"""

from typing import List, Dict, Iterator
import yaml, os, pdb, datetime, collections, json, pymongo, time
import streamlit as st; ss = st.session_state

from flowagent.data import (
    Config, DataManager, Workflow
)
from flowagent.utils import LLM_CFG

def debug_print_infos() -> None:
    print(f"[DEBUG] Conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    print(f"  > cfg.bot_pdl_controllers: {ss.cfg.bot_pdl_controllers}")

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
