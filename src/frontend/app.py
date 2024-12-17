"""
Run::
    streamlit run run_flowagent_ui2.py --server.port 8501 -- --config=ui_dev.yaml

@241212
- [x] #bug move `from .pages.page_single import main_single` to `setup_page()`
- [x] #feat config visible pages for different users (SUPERVISED_USERS)
"""

import traceback

import streamlit as st


ss = st.session_state
from common import init_loguru_logger
from flowagent.data import Config, DataManager

from .common.util_st import init_resource


SUPERVISED_USERS = ["Unknown", "easonsshi", "ianxxu", "tristanli", "siqiicai"]


def setup_basic(config_version: str):
    init_resource()  # headers, user_identity
    if "logger" not in ss:
        ss.logger = init_loguru_logger(DataManager.DIR_ui_log)
    # logger, config and data_manager
    if "cfg" not in ss:
        ss.cfg = Config.from_yaml(DataManager.normalize_config_name(config_version))
    if "data_manager" not in ss:
        ss.data_manager = DataManager(ss.cfg)


def setup_page(page_default_index: int = 0):
    from .pages.page_inspect import main_inspect
    from .pages.page_multi import main_multi
    from .pages.page_single import main_single

    available_pages = ["👤 Single", "👥 Multiple"]
    if ss.user_identity["staffname"] in SUPERVISED_USERS:
        available_pages += ["🔍 Inspect"]
    page = st.sidebar.selectbox("Select Mode", available_pages, index=page_default_index)
    st.sidebar.markdown("---")

    match page:
        case "👤 Single":
            main_single()
        case "👥 Multiple":
            main_multi()
        case "🔍 Inspect":
            main_inspect()
        case _:
            raise NotImplementedError


def main(config_version: str = "default.yaml", page_default_index: int = 0):
    setup_basic(config_version)
    try:
        setup_page(page_default_index)
    except Exception as e:
        st.image("https://media1.tenor.com/m/t7_iTN0iYekAAAAd/sad-sad-cat.gif")
        st.error(f"Oops, something funny happened with a {type(e).__name__}", icon="😿")
        print(traceback.format_exc())
