""" 
@241210
- [x] merge from conv_ui
@241211
- [x] #bug model the dependncy between select_col3~5 (selected_workflow_dataset, selected_pdl_version, selected_workflow_name)
- [x] #feat user_additional_constraints

todos
"""
import streamlit as st; ss = st.session_state
from .data_single import (
    get_template_name_list, get_model_name_list, get_workflow_dirs, get_workflow_names_map, 
    refresh_session_single, debug_print_infos_single
)
from flowagent.data import Config, DataManager

def init_sidebar():
    """Init the sidebar of single workflow"""
    config: Config = ss.cfg

    _model_names = get_model_name_list()
    _template_names = get_template_name_list()
    # _workflow_dirs = get_workflow_dirs()
    _workflow_names_map, _ = get_workflow_names_map()
    _workflow_datasets = list(_workflow_names_map.keys())
    
    # set the shown model names
    if config.ui_available_models:
        assert all(i in _model_names for i in config.ui_available_models), f"config models: {config.ui_available_models} not in _model_names: {_model_names}"
        LIST_shown_models = config.ui_available_models
    else:
        LIST_shown_models = _model_names
    # set the shown template names
    if config.ui_available_templates:
        assert all(i in _template_names for i in config.ui_available_templates), f"config templates: {config.ui_available_templates} not in _template_names: {_template_names}"
        LIST_shown_templates = config.ui_available_templates
    else:
        LIST_shown_templates = _template_names
    # set the shown workflow datasets
    if config.ui_available_workflow_datasets:
        LIST_shown_workflow_datasets = config.ui_available_workflow_datasets
    else:
        LIST_shown_workflow_datasets = _workflow_datasets
    
    with st.sidebar:
        select_col1, select_col2 = st.columns(2)
        with select_col1:
            st.selectbox(
                '选择模型',
                options=LIST_shown_models,
                key="selected_model_name",
                on_change=refresh_session_single,
                index=LIST_shown_models.index(config.ui_default_model)  # "default"
            )
        with select_col2:
            st.selectbox(
                '选择模板',
                options=LIST_shown_templates,
                key="selected_template_fn",
                index=LIST_shown_templates.index(config.ui_default_template),
                on_change=refresh_session_single
            )
        
        select_col3, select_col4, select_col5 = st.columns(3)
        with select_col3:
            st.selectbox(
                '选择数据集',
                options=LIST_shown_workflow_datasets,
                key="selected_workflow_dataset",
                index=LIST_shown_workflow_datasets.index(config.ui_default_workflow_dataset),
                on_change=update_workflow_dependencies
            )
        with select_col4:
            st.selectbox(
                '选择画布版本',
                options=get_workflow_dirs(ss.selected_workflow_dataset),
                key="selected_pdl_version",
                format_func=lambda x: x.split("/")[-1],     # NOTE: only show the last subdir
                on_change=update_version_dependencies
            )
        with select_col5:
            st.selectbox(
                '选择画布',
                options=_workflow_names_map[ss.selected_workflow_dataset],
                key="selected_workflow_name",
                index=0,        # default to choose the first one
                on_change=refresh_session_single
            )
        
        # st.divider()
        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            st.button(
                '重置对话',
                on_click=refresh_session_single
            )
        with button_col2:
            st.link_button(
                '问题反馈',
                "https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPI6WfByux6S2abI1stST?scode=AJEAIQdfAAolOjFcj8AcMATAZtAPI&tab=dyka3y"
            )
        with button_col3:
            st.button(
                'DEBUG',
                on_click=debug_print_infos_single,
            )

        with st.expander(f"⚙️ 自定义配置", expanded=False):
            st.text_area(
                "添加你对于PDL流程的额外约束", height=100, 
                key="user_additional_constraints", 
                placeholder="e.g. 当切换医院的时候, 默认科室不变. "
            )
            if st.button("应用"):
                if not ss.user_additional_constraints:
                    st.warning("请填写自定义约束")
                else:
                    config.ui_user_additional_constraints = ss.user_additional_constraints
                    refresh_session_single()

def update_workflow_dependencies():
    """Update dependencies when selected_workflow_dataset changes."""
    _workflow_names_map, _ = get_workflow_names_map()
    ss.selected_pdl_version = get_workflow_dirs(ss.selected_workflow_dataset)[0]  # Set to first version
    ss.selected_workflow_name = _workflow_names_map[ss.selected_workflow_dataset][0]  # Set to first workflow
    refresh_session_single()

def update_version_dependencies():
    """Update dependencies when selected_pdl_version changes."""
    _workflow_names_map, _ = get_workflow_names_map()
    ss.selected_workflow_name = _workflow_names_map[ss.selected_workflow_dataset][0]  # Set to first workflow
    refresh_session_single()

def post_sidebar():
    """
    Need: ss.controllers
    """
    with st.sidebar:
        # show the controllers
        cols = st.columns(3)
        for index, controller in enumerate(ss.cfg.bot_pdl_controllers):
            col = cols[index % 3]
            with col:
                controller['is_activated'] = st.checkbox(
                    controller['name'],
                    value=controller.get('is_activated', True),
                    on_change=refresh_session_single
                )

        # show the PDL and template
        st.divider()
        data_manager: DataManager = ss.data_manager
        with open(f"{data_manager.DIR_template}/{ss.selected_template_fn}", "r") as f:
            template = f.read()
        
        # show the PDL, can be got with single_register
        with st.expander(f"🔍 PDL", expanded=False):
            st.code(f"{ss.client.pdl_str}", language="plaintext")
        with st.expander(f"🔍 Template", expanded=False):
            st.code(f"{template}", language="plaintext")
        
        # show the user identity
        st.divider()
        st.info(f"- sessionid: {ss.session_id}\n- name: {ss.user_identity['staffname']}")
