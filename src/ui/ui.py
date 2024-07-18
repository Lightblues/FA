import time
import streamlit as st
from .datamodel import refresh_conversation, refresh_all, get_workflow_name_list

def init_page():
    st.set_page_config(
        page_title="PDL Test",
        page_icon="🍊",
        initial_sidebar_state="auto",
        # menu_items={
        #     'Get Help': 'https://www.extremelycoolapp.com/help',
        #     'Report a bug': "https://www.extremelycoolapp.com/bug",
        #     'About': "# This is a header. This is an *extremely* cool app!"
        # }
    )
    st.title('️🍊 PDL Test')
    return

def init_sidebar():
    with st.sidebar:
        workflow_names = get_workflow_name_list()
        st.selectbox(
            '选择画布',
            options=workflow_names,
            key="workflow_name",                # NOTE: set -> st.session_state.workflow_name
            on_change=lambda: refresh_all()
        )
        
        st.divider()
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            st.button(
                '重置对话',
                on_click=lambda: refresh_conversation()
            )
        with button_col2:
            st.link_button(
                '问题反馈',
                "https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPI6WfByux6S2abI1stST?scode=AJEAIQdfAAolOjFcj8AcMATAZtAPI&tab=dyka3y"
            )
