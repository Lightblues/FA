"""
@241211
- [x] modify from conv_ui
@241212
- [x] #bug fix toggle ("启用工具") and checkbox ("选择数据集") configs
    ref: https://docs.streamlit.io/develop/api-reference/widgets/st.toggle
    see `_collect_ui_config_tools` and `_collect_ui_config_workflows`
    NOTE: the exec sequence of `res = st.toggle(..., key=..., on_change=...)`:
    1. set the `key`;
    2. `on_change` callback will be called;
    3. the `res` will be returned.

todos
"""

import streamlit as st


ss = st.session_state
from flowagent.data import Config, DataManager

from .data_multi import debug_print_infos_multi, refresh_session_multi
from .data_single import (
    get_model_name_list,
    get_template_name_list,
    get_workflow_names_map,
)


def init_sidebar():
    """Init the sidebar of multi workflow"""
    config: Config = ss.cfg

    _model_names = get_model_name_list()
    _template_names = get_template_name_list()
    _workflow_names_map, _ = get_workflow_names_map()
    _workflow_datasets = list(_workflow_names_map.keys())

    # set the shown model names
    if config.mui_available_models:
        assert all(
            i in _model_names for i in config.mui_available_models
        ), f"config models: {config.mui_available_models} not in _model_names: {_model_names}"
        LIST_shown_models = config.mui_available_models
    else:
        LIST_shown_models = _model_names
    # set the shown template names
    if config.mui_agent_main_available_templates:
        assert all(
            i in _template_names for i in config.mui_agent_main_available_templates
        ), f"config templates: {config.mui_agent_main_available_templates} not in _template_names: {_template_names}"
        LIST_shown_templates = config.mui_agent_main_available_templates
    else:
        LIST_shown_templates = _template_names
    if config.mui_agent_workflow_available_templates:
        assert all(
            i in _template_names for i in config.mui_agent_workflow_available_templates
        ), f"config templates: {config.mui_agent_workflow_available_templates} not in _template_names: {_template_names}"
        LIST_shown_workflow_templates = config.mui_agent_workflow_available_templates
    else:
        LIST_shown_workflow_templates = _template_names
    # set the shown workflow datasets
    if config.ui_available_workflow_datasets:
        LIST_shown_workflow_datasets = config.ui_available_workflow_datasets
    else:
        LIST_shown_workflow_datasets = _workflow_datasets

    with st.sidebar:
        select_col1, select_col2 = st.columns(2)
        with select_col1:
            # refresh main & all workflow agents
            st.selectbox(
                "选择main-agent模型",
                options=LIST_shown_models,
                key="selected_mui_agent_main_llm_name",
                on_change=refresh_session_multi,
                index=LIST_shown_models.index(config.mui_agent_main_default_model),  # "default"
            )
        with select_col2:
            # only refresh the main agent
            st.selectbox(
                "选择main-agent模板",
                options=LIST_shown_templates,
                key="selected_mui_agent_main_template_fn",
                index=LIST_shown_templates.index(config.mui_agent_main_default_template),
                on_change=refresh_session_multi,
            )

        select_col3, select_col4 = st.columns(2)
        with select_col3:
            st.selectbox(
                "选择workflow-agent模型",
                options=LIST_shown_models,
                key="selected_mui_agent_workflow_llm_name",
                on_change=refresh_session_multi,
                index=LIST_shown_models.index(config.mui_agent_main_default_model),  # "default"
            )
        with select_col4:
            # only refresh the main agent
            st.selectbox(
                "选择workflow-agent模板",
                options=LIST_shown_workflow_templates,
                key="selected_mui_workflow_main_template_fn",
                index=LIST_shown_workflow_templates.index(config.mui_agent_workflow_default_template),
                on_change=refresh_session_multi,
            )

        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            st.button("重置对话", on_click=refresh_session_multi)
        with button_col2:
            st.link_button(
                "问题反馈",
                "https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPI6WfByux6S2abI1stST?scode=AJEAIQdfAAolOjFcj8AcMATAZtAPI&tab=dyka3y",
            )
        with button_col3:
            st.button(
                "DEBUG",
                on_click=debug_print_infos_multi,
            )

        # show the tools
        st.markdown("启用工具")
        cols = st.columns(3)
        for index, tool in enumerate(ss.tools):
            col = cols[index % 3]
            with col:
                # tool["is_enabled"] = ... NOTE: `tool["is_enabled"]` will be updated by `refresh_session_multi`
                st.toggle(
                    label=tool["name"],
                    value=tool["is_enabled"],
                    key=f"tool_toggle_{tool['name']}",
                    on_change=refresh_session_multi,
                )

        st.divider()
        # show the workflows
        select_col5, select_col6 = st.columns(2)
        with select_col5:
            st.selectbox(
                "选择数据集",
                options=LIST_shown_workflow_datasets,
                key="selected_workflow_dataset",
                index=LIST_shown_workflow_datasets.index(config.mui_default_workflow_dataset),
                on_change=update_workflow_dependencies,
            )

        setup_workflow_infos()

        cols = st.columns(3)
        for index, w in enumerate(ss.cfg.mui_workflow_infos):  # [{name, task_description, is_activated}]
            col = cols[index % 3]
            with col:
                # w['is_activated'] = ... NOTE: `w['is_activated']` will be updated by `refresh_session_multi`
                st.checkbox(
                    w["name"],
                    value=w["is_activated"],
                    key=f"workflow_checkbox_{w['name']}",
                    on_change=refresh_session_multi,
                )


def setup_workflow_infos(force_refresh: bool = False):
    """Set cfg.mui_workflow_infos"""
    # 1. set default workflow_infos
    if (not ss.cfg.mui_workflow_infos) or force_refresh:
        ss.cfg.workflow_dataset = ss.selected_workflow_dataset  # NOTE to update the workflow_dataset
        ss.cfg.mui_workflow_infos = list(DataManager(ss.cfg).workflow_infos.values())
        for w in ss.cfg.mui_workflow_infos:
            w["is_activated"] = True
    # 2. filter the available workflows
    if ss.cfg.mui_available_workflows:
        workflow_names = [w["name"] for w in ss.cfg.mui_workflow_infos]
        assert all(w in workflow_names for w in ss.cfg.mui_available_workflows)
        ss.cfg.mui_workflow_infos = [w for w in ss.cfg.mui_workflow_infos if w["name"] in ss.cfg.mui_available_workflows]


def update_workflow_dependencies():
    setup_workflow_infos(force_refresh=True)
    refresh_session_multi()


def post_sidebar():
    with st.sidebar:
        # show the user identity
        st.divider()
        st.info(f"- sessionid: {ss.session_id}\n- name: {ss.user_identity['staffname']}")
