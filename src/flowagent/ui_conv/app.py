""" 
Run::
    cd /mnt/huabu/src
    streamlit run run_flowagent_ui.py --server.port 8501 -- --config=ui_dev.yaml
"""
import streamlit as st; self = st.session_state
from ..data import Config, DataManager
from .page_single_workflow import main_single
from .page_multi_workflow import main_multi
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
    # useful infos
    init_resource()
    
    # config and data_manager
    if "config" not in self:
        self.cfg = Config.from_yaml(DataManager.normalize_config_name(config_name=config_version))
        print(f"[INFO] config: {self.cfg}")
    if "data_manager" not in self:
        self.data_manager = DataManager(self.cfg)
    
    page = st.sidebar.selectbox("Select Mode", ["👤 Single", "👥 Multiple", ])
    st.sidebar.markdown("---")
    
    if page == "👤 Single": main_single()
    elif page == "👥 Multiple": main_multi()