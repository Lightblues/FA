import time
import streamlit as st
from engine_v1.common import LLM_CFG
from engine_v1.datamodel import PDL
from .datamodel import (
    refresh_conversation, refresh_bot, refresh_pdl, 
    get_workflow_name_list, get_template_name_list, get_model_name_list, get_workflow_dir_list, get_workflow_info_dict, 
)


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
    LIST_template_names = get_template_name_list()
    LIST_model_names = get_model_name_list()
    LIST_workflow_dirs, DICT_workflow_info = get_workflow_info_dict()
    if "DICT_workflow_info" not in st.session_state:
        st.session_state.DICT_workflow_info = DICT_workflow_info
    
    with st.sidebar:
        select_col1, select_col2 = st.columns(2)
        with select_col1:
            st.selectbox(
                '选择模型',
                options=LIST_model_names,
                key="model_name",                # NOTE: set -> st.session_state.model_name
                on_change=refresh_bot,
                index=LIST_model_names.index("qwen2_72B")
            )
        with select_col2:
            st.selectbox(
                '选择模板',
                options=LIST_template_names,
                key="template_fn",                # NOTE: set -> st.session_state.template_fn
                on_change=refresh_bot
            )
        
        select_col3, select_col4 = st.columns(2)
        with select_col3:
            st.selectbox(
                '选择画布目录',
                options=LIST_workflow_dirs,
                key="workflow_dir",                # NOTE: set -> st.session_state.workflow_dir
                format_func=lambda x: x.split("/")[-1],     # NOTE: only show the last subdir
                on_change=lambda: refresh_pdl(dir_change=True)
            )
        with select_col4:
            st.selectbox(
                '选择画布',
                options=DICT_workflow_info[st.session_state.workflow_dir],      # change workflow_name when changing workflow_dir!
                key="workflow_name",                # NOTE: set -> st.session_state.workflow_name
                index=0,        # default to choose the first one
                on_change=refresh_pdl
            )
        
        st.divider()
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

        st.divider()
        pdl = PDL()
        pdl.load_from_file(f"{st.session_state.workflow_dir}/{st.session_state.workflow_name}.txt")
        with st.expander(f"PDL", expanded=True):
            # st.session_state.bot.pdl.to_str()}
            st.text(f"{pdl.to_str()}")
