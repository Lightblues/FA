""" 
Run::
    streamlit run run_flowagent_ui2.py --server.port 8501 -- --config=ui_dev.yaml
"""
import streamlit as st; ss = st.session_state
from flowagent.data import Config, DataManager, init_loguru_logger
if "logger" not in ss: ss.logger = init_loguru_logger(DataManager.DIR_ui_log)
from .page_single import main_single
from .page_multi import main_multi
from .page_inspect import main_inspect
from .common.util_st import init_resource

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


def main(config_version:str="default.yaml", page_default_index:int=0):
    # BUG: 1) page_single_workflow 中需要初始化的 logger, 因此尝试放在开头初始化; 2) 但发现这里也要接一个? 不然刷新页面之后会提示找不到 ss.logger
    if "logger" not in ss: ss.logger = init_loguru_logger(DataManager.DIR_ui_log)
    init_resource()  # headers, user_identity
    
    # config and data_manager
    if "cfg" not in ss:
        ss.cfg = Config.from_yaml(DataManager.normalize_config_name(config_version))
        # print(f"[INFO] config: {ss.cfg}")
    if "data_manager" not in ss:
        ss.data_manager = DataManager(ss.cfg)
    
    page = st.sidebar.selectbox("Select Mode", ["👤 Single", "👥 Multiple", "🔍 Inspect"], index=page_default_index)
    st.sidebar.markdown("---")
    
    match page:
        case "👤 Single": main_single()
        case "👥 Multiple": main_multi()
        case "🔍 Inspect": main_inspect()
        case _: raise NotImplementedError
