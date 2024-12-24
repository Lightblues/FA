"""Data for mutli-agent

- [ ] can also implemented as service/backend

"""

import json

import streamlit as st


ss = st.session_state
from fa_core.common import Config
from fa_core.tools import TOOLS_MAP

from .data_single import get_session_id


def debug_print_infos_multi() -> None:
    print(f"[DEBUG] Conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    print(f"  cfg.mui_workflow_infos: {ss.cfg.mui_workflow_infos}")
    print(f"  cfg.ui_tools: {ss.cfg.ui_tools}")
    print(f"  client.curr_status: {ss.client.curr_status}")


def init_tools():
    """Set ss.tools from ss.cfg.ui_tools.
    1. check the validity of the tools
    2. set the default value of is_enabled to True
    """
    if "tools" not in ss:
        for t in ss.cfg.ui_tools:
            assert t["name"] in TOOLS_MAP, f"{t['name']} not in available tools {TOOLS_MAP.keys()}"
            if "is_enabled" not in t:
                t["is_enabled"] = True
        ss.tools = ss.cfg.ui_tools


def _collect_ui_config_tools():
    """Collect `cfg.ui_tools` from ss.tool_toggle_<tool_name>"""
    for t in ss.cfg.ui_tools:
        t["is_enabled"] = ss.get(f"tool_toggle_{t['name']}", True)
    return ss.cfg.ui_tools


def _collect_ui_config_workflows():
    """Collect `cfg.mui_workflow_infos` from ss.workflow_checkbox_<workflow_name>"""
    for w in ss.cfg.mui_workflow_infos:
        # NOTE: use `get` to avoid KeyError. see `update_workflow_dependencies` in ui_multi.py
        w["is_activated"] = ss.get(f"workflow_checkbox_{w['name']}", True)
    return ss.cfg.mui_workflow_infos


def refresh_session_multi():
    """Refresh the config and init new session
    NOTE: will reset a new session!

    Used config:
        ``Workflow``: workflow_type, workflow_id, pdl_version
            mode | exp_mode | user_mode
        ``UISingleBot``: bot_template_fn, bot_llm_name, bot_retry_limit
        ``RequestTool``: api_entity_linking
            ``EntityLinker``: api_entity_linking_llm, api_entity_linking_template
        ``controllers``: bot_pdl_controllers
    """
    # 1. collect the selected config
    cfg: Config = ss.cfg
    cfg.mui_agent_main_llm_name = ss.selected_mui_agent_main_llm_name
    cfg.mui_agent_main_template_fn = f"{ss.selected_mui_agent_main_template_fn}"

    cfg.bot_template_fn = f"{ss.selected_mui_workflow_main_template_fn}"
    cfg.bot_llm_name = ss.selected_mui_agent_workflow_llm_name

    cfg.workflow_dataset = ss.selected_workflow_dataset

    _collect_ui_config_tools()
    _collect_ui_config_workflows()

    # 2. init session!
    if "session_id" in ss and ss.session_id:
        # NOTE: disconnect the old session!
        ss.client.multi_disconnect(ss.session_id)
    ss.session_id = get_session_id()
    ss.conv = ss.client.multi_register(ss.session_id, ss.cfg, ss.user_identity)
