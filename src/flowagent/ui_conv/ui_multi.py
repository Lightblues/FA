import streamlit as st; ss = st.session_state
from ..data import Config, Conversation, Message, Role
from .data_multi import refresh_conversation, refresh_main_agent, debug_print_infos, update_workflow_agents, update_workflow_dataset
from .data_single import get_model_name_list, get_template_name_list, get_workflow_names_map

def init_sidebar():
    """Init the sidebar of multi workflow
    """
    config: Config = ss.cfg
    
    _model_names = get_model_name_list()
    _template_names = get_template_name_list()

    # set the shown model names
    if config.mui_available_models:
        assert all(i in _model_names for i in config.mui_available_models), f"config models: {config.mui_available_models} not in _model_names: {_model_names}"
        LIST_shown_models = config.mui_available_models
    else:
        LIST_shown_models = _model_names
    # set the shown template names
    if config.mui_agent_main_available_templates:
        assert all(i in _template_names for i in config.mui_agent_main_available_templates), f"config templates: {config.mui_agent_main_available_templates} not in _template_names: {_template_names}"
        LIST_shown_templates = config.mui_agent_main_available_templates
    else:
        LIST_shown_templates = _template_names
    if config.mui_agent_workflow_available_templates:
        assert all(i in _template_names for i in config.mui_agent_workflow_available_templates), f"config templates: {config.mui_agent_workflow_available_templates} not in _template_names: {_template_names}"
        LIST_shown_workflow_templates = config.mui_agent_workflow_available_templates
    else:
        LIST_shown_workflow_templates = _template_names

    _workflow_names_map, _ = get_workflow_names_map()
    _workflow_datasets = list(_workflow_names_map.keys())
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
                '选择main-agent模型',
                options=LIST_shown_models,
                key="selected_mui_agent_main_llm_name",
                on_change=refresh_main_agent,
                index=LIST_shown_models.index(config.mui_agent_main_default_model)  # "default"
            )
        with select_col2:
            # only refresh the main agent
            st.selectbox(
                '选择main-agent模板',
                options=LIST_shown_templates,
                key="selected_mui_agent_main_template_fn",
                index=LIST_shown_templates.index(config.mui_agent_main_default_template),
                on_change=refresh_main_agent
            )
        
        select_col3, select_col4 = st.columns(2)
        with select_col3:
            st.selectbox(
                '选择workflow-agent模型',
                options=LIST_shown_models,
                key="selected_mui_agent_workflow_llm_name",
                on_change=update_workflow_agents,
                index=LIST_shown_models.index(config.mui_agent_main_default_model)  # "default"
            )
        with select_col4:
            # only refresh the main agent
            st.selectbox(
                '选择workflow-agent模板',
                options=LIST_shown_workflow_templates,
                key="selected_mui_workflow_main_template_fn",
                index=LIST_shown_workflow_templates.index(config.mui_agent_workflow_default_template),
                on_change=update_workflow_agents
            )

        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            st.button(
                '重置对话',
                on_click=refresh_conversation
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

        # show the tools
        st.markdown("启用工具")
        cols = st.columns(3)
        for index, tool_name in enumerate(ss.tools.keys()):
            col = cols[index % 3]
            with col:
                ss.tools[tool_name]["is_enabled"] = st.toggle(
                    tool_name,
                    value=ss.tools[tool_name]["is_enabled"]
                )
        
        st.divider()
        # show the workflows
        select_col5, select_col6 = st.columns(2)
        with select_col5:
            st.selectbox(
                '选择数据集',
                options=LIST_shown_workflow_datasets,
                key="selected_workflow_dataset",
                index=LIST_shown_workflow_datasets.index(config.workflow_dataset),
                on_change=update_workflow_dataset,
            )
        
        update_workflow_dataset()
        cols = st.columns(3)
        for index, w in enumerate(ss.workflow_infos):   # [{name, description}]
            col = cols[index % 3]
            with col:
                w['is_activated'] = st.checkbox(
                    w['name'],
                    value=w['is_activated']
                )


def post_sidebar():
    with st.sidebar:

        # show the user identity
        st.divider()
        st.info(f"- sessionid: {ss.conv.conversation_id}\n- name: {ss.user_identity['staffname']}")
