"""
Run::
    streamlit run run_demo_frontend.py --server.port 8501 -- --config=ui_dev.yaml
    streamlit run run_demo_frontend.py --server.port 8502 -- --config=dev.yaml --page_default_index=0

@241212
- [x] #bug move `from .pages.page_single import main_single` to `setup_page()`
- [x] #feat config visible pages for different users (SUPERVISED_USERS)
"""

import traceback

import streamlit as st


ss = st.session_state
from fa_core.common import Config, init_loguru_logger
from fa_core.data import FADataManager

from .common.util_st import init_resource


SUPERVISED_USERS = ["Unknown", "easonsshi", "ianxxu", "tristanli", "siqiicai"]
PAGE_URL_NAME_MAPPING = {"single": "👤 Single", "multiple": "👥 Multiple", "inspect": "🔍 Inspect"}


def setup_basic(config_version: str):
    init_resource()  # headers, user_identity
    if "logger" not in ss:
        ss.logger = init_loguru_logger(FADataManager.DIR_ui_log)
    # logger, config and data_manager
    if "cfg" not in ss:
        ss.cfg = Config.from_yaml(config_version)
    if "data_manager" not in ss:
        ss.data_manager = FADataManager(workflow_dataset=ss.cfg.workflow_dataset)


def setup_page():
    from .pages.page_inspect import main_inspect
    from .pages.page_multi import main_multi
    from .pages.page_single import main_single

    # 1. all the available pages (URL names)
    # available_pages = ["single", "multiple"]
    available_pages = ["single"]
    if ss.user_identity["staffname"] in SUPERVISED_USERS:
        available_pages += ["inspect"]

    # 2. get the page from URL
    page_from_url = st.query_params.get("page", None)
    if page_from_url in available_pages:
        initial_page = page_from_url
    else:
        initial_page = ss.cfg.st_default_page if ss.cfg.st_default_page in available_pages else available_pages[0]

    # 3. display the selectbox with friendly names
    display_names = [PAGE_URL_NAME_MAPPING[p] for p in available_pages]
    selected_display = st.sidebar.selectbox(
        "Select Mode",
        display_names,
        index=available_pages.index(initial_page),
        format_func=lambda x: x,  # directly show the friendly name
    )
    # convert the display name to URL name
    page = next(url_name for url_name, display_name in PAGE_URL_NAME_MAPPING.items() if display_name == selected_display)

    # 4. update the URL parameter
    st.query_params["page"] = page

    st.sidebar.markdown("---")

    match page:
        case "single":
            main_single()
        case "multiple":
            main_multi()
        case "inspect":
            main_inspect()
        case _:
            raise NotImplementedError


def main(config_version: str = "default.yaml"):
    setup_basic(config_version)
    try:
        setup_page()
    except Exception as e:
        st.image("https://media1.tenor.com/m/t7_iTN0iYekAAAAd/sad-sad-cat.gif")
        st.error(f"Oops, something funny happened with a {type(e).__name__}", icon="😿")
        print(traceback.format_exc())
