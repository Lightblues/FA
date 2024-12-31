"""
Inspect the history conversations.

Display logic:
1. select mode: single or multi;
2. select session_id, then show conversation and config;
3. inspect specifig utterance infos;

@241208 display v0
- [x] implement basic UI
@241226
- [x] add a button to select db_collection!
- [x] add a `select_by` to select exp_id/session_id!  -- stay simply!
@241227
- [x] refactor!
- [x] add PDL to the sidebar
@241231
- [x] #fix add `len(ss.latest_sessionids) == 0` check to avoid error!
"""

from typing import List
from loguru import logger
import streamlit as st
import pandas as pd

ss = st.session_state
from fa_core.common import Config, DBUtils, get_session_id
from fa_server import FrontendClient
from fa_server.typings import InspectGetWorkflowQuery


def get_latest_sessionids() -> List[str]:
    """set ss.latest_sessionids."""
    db_utils: DBUtils = ss.db_utils
    query = {}
    if ss.exp_version:
        query["exp_version"] = ss.exp_version
    limit = ss.get("exp_limit", 100)

    # 1. ss.latest_sessionids, ss.latest_expids
    _res = db_utils.find_sessions_by_query(query=query, collection=ss.db_collection, limit=limit)
    ss.latest_sessionids = [item["session_id"] for item in _res]
    ss.latest_expids = [item["exp_id"] for item in _res]
    # 2. ss.sessionid_expid_map
    ss.sessionid_expid_map = {item["session_id"]: item["exp_id"] for item in _res}
    ss.expid_sessionid_map = {item["exp_id"]: item["session_id"] for item in _res}
    # 3. ss.total_exp_count
    ss.total_exp_count = db_utils.count_documents_by_query(query=query, collection=ss.db_collection)

    logger.info(f"got {len(ss.latest_sessionids)} sessions from {ss.db_collection} with query: {query}")
    return ss.latest_sessionids


def sidebar_setup_db(cfg: Config, db_utils: DBUtils):
    """Set up the db_collection, exp_version, exp_limit

    Ensure:
        `latest_sessionids` is set!
    """
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.selectbox(
            "1️⃣ Select db_collection",
            options=cfg.db_available_collections,
            index=0
            if cfg.st_default_db_collection not in cfg.db_available_collections
            else cfg.db_available_collections.index(cfg.st_default_db_collection),
            key="db_collection",
            on_change=get_latest_sessionids,
        )
    with col2:
        # set options and index
        if cfg.db_available_exp_versions:
            _exp_versions = cfg.db_available_exp_versions
        else:
            _exp_versions = db_utils.get_exp_versions(ss.db_collection)
        _exp_versions += [""]
        if (not cfg.st_default_exp_version) or (cfg.st_default_exp_version not in cfg.db_available_exp_versions):
            _index = 0
        else:
            _index = cfg.db_available_exp_versions.index(cfg.st_default_exp_version)
        st.selectbox(
            "exp_version",
            options=_exp_versions,
            index=_index,
            key="exp_version",
            on_change=get_latest_sessionids,
        )
    with col3:
        st.number_input(
            "exp_limit",
            key="exp_limit",
            value=100,
            min_value=1,
            max_value=500,
            on_change=get_latest_sessionids,
        )
    # ensure `latest_sessionids` is set!
    if "latest_sessionids" not in ss:
        get_latest_sessionids()


def sidebar_select_sessionid() -> bool:
    """Select session_id by `selected_session_idx` or `selected_exp_idx`

    Ensure:
        `selected_session_id` is set!

    NOTE:
        - two selection modes: session_id & exp_id!
    """
    col1, col2, col3 = st.columns([4, 1, 2])
    # NOTE: use `on_change` to update `ss.selected_session_id` & `ss.selected_exp_id`
    with col1:
        select_by = st.selectbox("2️⃣ Select session by", ["session_id", "exp_id"], index=0)
        if select_by == "session_id":

            def on_change_session_idx():
                ss.selected_session_id = ss.latest_sessionids[ss.selected_session_idx]
                ss.selected_exp_id = ss.sessionid_expid_map[ss.selected_session_id]

            st.selectbox(
                "session_id",
                options=list(range(len(ss.latest_sessionids))),
                format_func=lambda x: ss.latest_sessionids[x],
                key="selected_session_idx",
                on_change=on_change_session_idx,
            )
            customized_session_id = st.text_input("Or input a customized session_id:")
            if customized_session_id:
                ss.selected_session_id = customized_session_id
                ss.selected_exp_id = ss.sessionid_expid_map[ss.selected_session_id]
        else:

            def on_change_exp_idx():
                ss.selected_exp_id = ss.latest_expids[ss.selected_exp_idx]
                ss.selected_session_id = ss.expid_sessionid_map[ss.selected_exp_id]

            st.selectbox(
                "exp_id",
                options=list(range(len(ss.latest_expids))),
                format_func=lambda x: ss.latest_expids[x],
                key="selected_exp_idx",
                on_change=on_change_exp_idx,
            )
            customized_exp_id = st.text_input("Or input a customized exp_id:")
            if customized_exp_id:
                ss.selected_exp_id = customized_exp_id
                ss.selected_session_id = ss.expid_sessionid_map[ss.selected_exp_id]

        # check the session_id & exp_id!!
        if len(ss.latest_sessionids) == 0:
            st.warning("No sessions found. Please select another db_collection/exp_version.")
            return -1
        if ("selected_session_id" not in ss) or (ss.selected_session_id not in ss.latest_sessionids):
            ss.selected_session_id = ss.latest_sessionids[0]
            ss.selected_exp_id = ss.sessionid_expid_map[ss.selected_session_id]

        with col3:
            st.write("")  # Add some vertical space
            st.button("Refresh", on_click=get_latest_sessionids)
            if st.button("⬆️ Prev", key="prev_session"):
                current_idx = ss.latest_sessionids.index(ss.selected_session_id)
                if current_idx > 0:
                    ss.selected_session_id = ss.latest_sessionids[current_idx - 1]
                    ss.selected_exp_id = ss.sessionid_expid_map[ss.selected_session_id]
                else:
                    st.warning("No previous session found.")
            if st.button("⬇️ Next", key="next_session"):
                current_idx = ss.latest_sessionids.index(ss.selected_session_id)
                if current_idx < len(ss.latest_sessionids) - 1:
                    ss.selected_session_id = ss.latest_sessionids[current_idx + 1]
                    ss.selected_exp_id = ss.sessionid_expid_map[ss.selected_session_id]
                else:
                    st.warning("No next session found.")

            st.selectbox(
                "display option",
                key="display_option",
                options=["Table", "Dataframe"],
            )
        return 0


def show_info():
    info_str = f"- exp_version: `{ss.exp_version}` (#exps: ${ss.total_exp_count}$) \n"
    info_str += f"- exp_id: `{ss.selected_exp_id}` \n"
    info_str += f"- session_id: `{ss.selected_session_id}` \n"
    st.info(info_str)


def show_conversation(df: pd.DataFrame):
    selected_columns = ["role", "content", "utterance_id", "llm_response"]
    df_selected = df[selected_columns].set_index("utterance_id")
    st.markdown(f"### Conversation")
    with st.expander("Details", expanded=True):
        if ss.display_option == "Dataframe":
            st.dataframe(df_selected)
        else:
            st.table(df_selected)
            # table is better for reading then st.dataframe!

    # show the utterance infos
    utterance_ids = df["utterance_id"].unique()
    with st.sidebar:
        selected_utterance_id = st.selectbox("3️⃣ Select utterance_id", options=utterance_ids)

    st.markdown(f"### Details of `utterance_id={selected_utterance_id}`")
    with st.expander("Details", expanded=False):
        if selected_utterance_id is not None:
            selected_row = df[df["utterance_id"] == selected_utterance_id].iloc[0]
            st.write(selected_row.to_dict())


def show_config(cfg: Config):
    st.markdown(f"### Configuration")
    with st.expander("Details"):
        st.write(cfg.model_dump())


def sidebar_show_pdl(exp_cfg: Config):
    st.divider()
    if "client" not in ss:
        ss.client = FrontendClient(backend_url=ss.cfg.backend_url)
    workflow = ss.client.inspect_get_workflow("xxx", exp_cfg.workflow_dataset, exp_cfg.workflow_id).workflow
    with st.expander(f"🔍 PDL", expanded=False):
        st.code(f"{workflow.pdl.to_str()}", language="plaintext")
    with st.expander(f"🔍 PDL.Procedure", expanded=False):
        st.code(f"{workflow.pdl.Procedure}", language="plaintext")

    # show the user identity
    st.divider()
    st.info(f"- name: {ss.user_identity['staffname']}")


def main_inspect():
    cfg: Config = ss.cfg
    if "db_utils" not in ss:
        ss.db_utils = DBUtils(mongo_uri=cfg.db_uri, db_name=cfg.db_name)
    db_utils: DBUtils = ss.db_utils

    with st.sidebar:
        # 1. select `db_collection`
        sidebar_setup_db(cfg, db_utils)
        # 2. select speicific `session_id`
        if sidebar_select_sessionid() != 0:
            return

    # ------------------ main --------------------
    if ("selected_session_id" not in ss) or (not ss.selected_session_id):
        st.warning("Please select a session_id first.")
        return
    exp_cfg, exp_conv = db_utils.get_data_by_sessionid(ss.selected_session_id, collection=ss.db_collection)
    if len(exp_conv.msgs) == 0:
        st.warning(f"Conversation `{ss.selected_session_id}` is empty.")
        return
    df = exp_conv.to_dataframe()

    # --- show info ---
    show_info()
    show_conversation(df)
    show_config(exp_cfg)

    with st.sidebar:
        sidebar_show_pdl(exp_cfg)
