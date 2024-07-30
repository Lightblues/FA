import streamlit as st


from engine_v2 import PDL, PDL_v2, PDLController, _DIRECTORY_MANAGER, Config
from .data import (
    get_template_name_list, get_model_name_list, get_workflow_info_dict, 
    refresh_bot, refresh_pdl, refresh_conversation
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
    config: Config = st.session_state.config
    
    LIST_template_names = get_template_name_list()
    LIST_model_names = get_model_name_list()
    
    # set the shown model names
    if config.available_models:
        _available_models = config.available_models
        print(f"available_models: {_available_models}")
        assert all(i in LIST_model_names for i in config.available_models)
        if type(_available_models) == list:
            LIST_model_names = config.available_models
        elif type(_available_models) == dict:
            LIST_model_names = list(_available_models.values())
    LIST_workflow_dirs, DICT_workflow_info = get_workflow_info_dict(config)
    if "DICT_workflow_info" not in st.session_state:
        st.session_state.DICT_workflow_info = DICT_workflow_info
        st.session_state.user_additional_constraints = None
    
    with st.sidebar:
        select_col1, select_col2 = st.columns(2)
        with select_col1:
            st.selectbox(
                '选择模型',
                options=LIST_model_names,
                key="model_name",                # NOTE: set -> st.session_state.model_name
                on_change=refresh_bot,
                index=LIST_model_names.index("default")
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
        
        with st.expander(f"⚙️ 自定义配置", expanded=False):
            st.text_area(
                "添加你对于PDL流程的额外约束", height=100, 
                key="user_additional_constraints", 
                placeholder="e.g. 当切换医院的时候, 默认科室不变. "
            )
            if st.button("应用"):
                if not st.session_state.user_additional_constraints:
                    st.warning("请填写自定义约束")
                else:
                    refresh_conversation()
                    # print(f"  <debug> user_additional_constraints: {st.session_state.user_additional_constraints}")

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
        # NOTE: init `pdl`
        if "pdl" not in st.session_state:
            assert hasattr(config, "pdl_version"), "`pdl_version` missing in config!"
            if config.pdl_version == "v1":
                _PDL = PDL
            elif config.pdl_version == "v2":
                _PDL = PDL_v2
            else: raise ValueError(f"Unknown PDL version: {config.pdl_version}")
            st.session_state.pdl = _PDL.load_from_file(f"{st.session_state.workflow_dir}/{st.session_state.workflow_name}.txt")
            st.session_state.pdl_controller = PDLController(st.session_state.pdl)
        with open(f"{_DIRECTORY_MANAGER.DIR_templates}/{st.session_state.template_fn}", "r") as f:     # pdl_fn = f"{st.session_state.workflow_dir}/{st.session_state.workflow_name}.txt"
            template = f.read()
        
        with st.expander(f"🔍 PDL", expanded=True):
            st.text(f"{st.session_state.pdl.to_str()}")
        with st.expander(f"🔍 Template", expanded=False):
            st.text(f"{template}")
