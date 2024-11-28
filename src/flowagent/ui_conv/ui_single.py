import datetime
import streamlit as st; ss = st.session_state
from .data_single import (
    get_template_name_list, get_model_name_list, get_workflow_dirs, get_workflow_names_map, 
    refresh_bot, refresh_workflow, debug_print_infos
)
from ..data import Config, Workflow, DataManager

def init_sidebar():
    """Init the sidebar of single workflow"""
    config: Config = ss.cfg

    _model_names = get_model_name_list()
    _template_names = get_template_name_list()
    _workflow_dirs = get_workflow_dirs()
    _workflow_names_map, _ = get_workflow_names_map()
    
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
    # set the shown workflow dirs
    if config.ui_available_workflow_dirs:
        assert all(i in _workflow_dirs for i in config.ui_available_workflow_dirs), f"config workflow_dirs: {config.ui_available_workflow_dirs} not in _workflow_dirs: {_workflow_dirs}"
        LIST_shown_dirs = config.ui_available_workflow_dirs
    else:
        LIST_shown_dirs = _workflow_dirs
    # set the shown workflow names
    # if config.ui_available_workflows:
    #     # for d, l in DICT_workflow_info.items():
    #     #     assert all(i in l for i in config.ui_available_workflows), f"config workflows: {config.ui_available_workflows} not in workflow_list: {l}"
    #     #     DICT_workflow_info[d] = config.ui_available_workflows
    #     pass
    
    with st.sidebar:
        select_col1, select_col2 = st.columns(2)
        with select_col1:
            st.selectbox(
                '选择模型',
                options=LIST_shown_models,
                key="selected_model_name",
                on_change=refresh_bot,
                index=LIST_shown_models.index(config.ui_default_model)  # "default"
            )
        with select_col2:
            st.selectbox(
                '选择模板',
                options=LIST_shown_templates,
                key="selected_template_fn",
                index=LIST_shown_templates.index(config.ui_default_template),
                on_change=refresh_workflow
            )
        
        select_col3, select_col4 = st.columns(2)
        with select_col3:
            st.selectbox(
                '选择画布版本',
                options=LIST_shown_dirs,
                key="selected_pdl_version",
                format_func=lambda x: x.split("/")[-1],     # NOTE: only show the last subdir
                on_change=refresh_workflow
            )
        with select_col4:
            st.selectbox(
                '选择画布',
                options=_workflow_names_map[ss.cfg.workflow_dataset],
                key="selected_workflow_name",
                index=0,        # default to choose the first one
                on_change=refresh_workflow
            )
        
        # st.divider()
        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            st.button(
                '重置对话',
                on_click=refresh_bot
            )
        with button_col2:
            st.link_button(
                '问题反馈',
                "https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPI6WfByux6S2abI1stST?scode=AJEAIQdfAAolOjFcj8AcMATAZtAPI&tab=dyka3y"
            )
        with button_col3:
            st.button(
                'DEBUG',
                on_click=debug_print_infos,
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
                    refresh_bot()


def post_sidebar():
    with st.sidebar:
        cols = st.columns(3)
        for index, controller in enumerate(ss.controllers.values()):
            col = cols[index % 3]
            with col:
                controller.is_activated = st.checkbox(
                    controller.name,
                    value=controller.is_activated
                )

        # show the PDL and template
        st.divider()
        data_manager: DataManager = ss.data_manager
        workflow: Workflow = ss.workflow
        with open(f"{data_manager.DIR_template}/{ss.selected_template_fn}", "r") as f:
            template = f.read()
        
        with st.expander(f"🔍 PDL", expanded=False):
            st.code(f"{workflow.pdl.to_str()}", language="plaintext")
        with st.expander(f"🔍 Template", expanded=False):
            st.code(f"{template}", language="plaintext")
        
        # show the user identity
        st.divider()
        st.info(f"- sessionid: {ss.conv.conversation_id}\n- name: {ss.user_identity['staffname']}")
