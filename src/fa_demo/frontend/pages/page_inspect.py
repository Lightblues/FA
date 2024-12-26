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
"""

from typing import List

import streamlit as st


ss = st.session_state
from fa_core.common import Config, DBUtils


def get_latest_sessionids(refresh: bool = False) -> List[str]:
    """set ss.latest_sessionids.
    NOTE: set refresh=True when ``ss.db_collection`` changes

    Args:
        refresh (bool, optional): weather to refresh cached data. Defaults to False.
    """
    if ("latest_sessionids" not in ss) or refresh:
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
    return ss.latest_sessionids


def main_inspect():
    cfg: Config = ss.cfg
    if "db_utils" not in ss:
        ss.db_utils = DBUtils()
    db_utils: DBUtils = ss.db_utils

    with st.sidebar:
        # 1. select `db_collection`
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.selectbox(
                "1️⃣ Select db_collection",
                options=cfg.db_available_collections,
                index=0
                if cfg.st_default_db_collection not in cfg.db_available_collections
                else cfg.db_available_collections.index(cfg.st_default_db_collection),
                key="db_collection",
                on_change=lambda: get_latest_sessionids(refresh=True),
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
                on_change=lambda: get_latest_sessionids(refresh=True),
            )
        with col3:
            st.number_input(
                "exp_limit",
                key="exp_limit",
                value=100,
                min_value=1,
                max_value=500,
                on_change=lambda: get_latest_sessionids(refresh=True),
            )

        # 2. select speicific `session_id`
        col1, col2, col3 = st.columns([2, 1, 1])
        get_latest_sessionids()
        with col1:
            select_by = st.selectbox("2️⃣ Select session by", ["session_id", "exp_id"], index=0)
            if select_by == "session_id":
                session_id = st.selectbox(
                    "session_id",
                    options=ss.latest_sessionids,
                )
                customized_session_id = st.text_input("Or input a customized session_id:")
                if customized_session_id:
                    session_id = customized_session_id
            else:
                exp_id = st.selectbox(
                    "exp_id",
                    options=ss.latest_expids,
                )
                customized_exp_id = st.text_input("Or input a customized exp_id:")
                if customized_exp_id:
                    exp_id = customized_exp_id
                session_id = ss.expid_sessionid_map[exp_id]
        with col3:
            st.write("")  # Add some vertical space
            st.button("Refresh", on_click=lambda: get_latest_sessionids(refresh=True))
            display_option = st.selectbox(
                "display option",
                options=["Table", "Dataframe"],
            )

    # ------------------ main --------------------
    if session_id:
        # 1. query conversation from db ; show the conversation
        cfg, conv = db_utils.get_data_by_sessionid(session_id, collection=ss.db_collection)
        if len(conv.msgs) == 0:
            st.warning(f"Conversation `{session_id}` is empty.")
            return
        df = conv.to_dataframe()
        selected_columns = ["role", "content", "utterance_id", "llm_response"]
        df_selected = df[selected_columns].set_index("utterance_id")
        st.markdown(f"### Conversation `{session_id}`")
        if display_option == "Dataframe":
            st.dataframe(df_selected)
        else:
            st.table(
                df_selected,
            )  # table is better for reading then st.dataframe!

        # 2. show the config
        st.markdown(f"### Configuration")
        with st.expander("Details"):
            st.write(cfg.model_dump())

        # 5. show the utterance infors
        utterance_ids = df["utterance_id"].unique()
        with st.sidebar:
            selected_utterance_id = st.selectbox("3️⃣ Select utterance_id", options=utterance_ids)

        st.markdown(f"### Details of `utterance_id={selected_utterance_id}`")
        with st.expander("Details", expanded=True):
            if selected_utterance_id is not None:
                selected_row = df[df["utterance_id"] == selected_utterance_id].iloc[0]
                st.write(selected_row.to_dict())

    with st.sidebar:
        st.divider()
        exp_id = ss.sessionid_expid_map[session_id]
        st.info(f"- selected session_id: `{session_id}` (exp_id: `{exp_id}`)\n- #exps of `exp_version={ss.exp_version}`: {ss.total_exp_count}")
