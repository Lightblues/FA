import streamlit as st; ss = st.session_state
import datetime
from ..data import Config, Conversation, Message, Role
from .data_multi import refresh_conversation, refresh_main_agent
from .data_single import get_model_name_list, get_template_name_list

def init_sidebar():
    """Init the sidebar of multi workflow
    TODO: select used workflows
    """
    config: Config = ss.cfg
    
    _model_names = get_model_name_list()
    _template_names = get_template_name_list()

    # set the shown model names
    if config.mui_available_models:
        assert all(i in _model_names for i in config.mui_available_models), f"config models: {config.ui_available_models} not in _model_names: {_model_names}"
        LIST_shown_models = config.mui_available_models
    else:
        LIST_shown_models = _model_names
    # set the shown template names
    if config.mui_available_templates:
        assert all(i in _template_names for i in config.mui_available_templates), f"config templates: {config.mui_available_templates} not in _template_names: {_template_names}"
        LIST_shown_templates = config.mui_available_templates
    else:
        LIST_shown_templates = _template_names

    with st.sidebar:
        select_col1, select_col2 = st.columns(2)
        with select_col1:
            st.selectbox(
                '选择模型',
                options=LIST_shown_models,
                key="selected_model_name",
                on_change=refresh_main_agent,
                index=LIST_shown_models.index(config.mui_default_model)  # "default"
            )
        with select_col2:
            st.selectbox(
                '选择模板',
                options=LIST_shown_templates,
                key="selected_template_fn",
                index=LIST_shown_templates.index(config.mui_default_template),
                on_change=refresh_main_agent  # sure?
            )
        

        button_col1, button_col2 = st.columns(2)
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
            
def post_sidebar():
    with st.sidebar:

        # show the user identity
        st.divider()
        st.info(f"- sessionid: {ss.conv.conversation_id}\n- name: {ss.user_identity['staffname']}")
