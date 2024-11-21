""" 
Run::
    cd /mnt/huabu/src
    streamlit run run_flowagent_ui.py --server.port 8501 -- --config=ui_dev.yaml
"""
import streamlit as st
st.set_page_config(
    page_title="PDL Agent",
    page_icon="🍊",
    initial_sidebar_state="auto",
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "mailto:easonsshi@tencent.com",
        # 'About': "# This is a header. This is an *extremely* cool app!"
    }
)
st.title('️🍊 PDL Agent')

from ..data import Config, DataManager
from .page_single_workflow import main_single
from .ui_data import init_resource

# def set_global_exception_handler(f):
#     from streamlit.runtime.scriptrunner.script_runner import handle_uncaught_app_exception
#     handle_uncaught_app_exception.__code__ = f.__code__

# def exception_handler(e):
#     import traceback
#     # Custom error handling
#     # st.image("https://media1.tenor.com/m/t7_iTN0iYekAAAAd/sad-sad-cat.gif")
#     st.error(f"Oops, something funny happened with a {type(e).__name__}", icon="😿")
#     print(traceback.format_exc())
#     st.warning(traceback.format_exc())

# set_global_exception_handler(exception_handler)


def main(config_version:str="default.yaml"):
    init_resource()
    if "config" not in st.session_state:
        st.session_state.config = Config.from_yaml(DataManager.normalize_config_name(config_name=config_version))
        print(f"[INFO] config: {st.session_state.config}")
    if "data_manager" not in st.session_state:
        st.session_state.data_manager = DataManager(st.session_state.config)
    
    page = st.sidebar.selectbox("Select Mode", ["👤 Single", "👥 Multip", ])
    st.sidebar.markdown("---")
    
    if page == "👤 Single": main_single()
    elif page == "👥 Multip": pass
