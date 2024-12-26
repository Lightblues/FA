"""
Inspect the history conversations.

Display logic:
1. select mode: single or multi;
2. select session_id, then show conversation and config;
3. inspect specifig utterance infos;

@241208 display v0
- [x] implement basic UI

- [ ] add a button to select db_collection!
"""

from typing import List

import streamlit as st


ss = st.session_state
from fa_core.common import Config

from ..common.util_db import DBUtils


def get_latest_sessionids(refresh: bool = False) -> List[str]:
    """set ss.latest_sessionids.
    NOTE: set refresh=True when ``ss.db_collection`` changes

    Args:
        refresh (bool, optional): weather to refresh cache_data. Defaults to False.
    """
    if ("latest_sessionids" not in ss) or refresh:
        db_utils: DBUtils = ss.db_utils
        # ss.latest_sessionids = db_utils.get_latest_sessionids(limit=10, collection=ss.db_collection)
        query = {}
        if ss.exp_version:
            query["exp_version"] = ss.exp_version
        ss.latest_sessionids = db_utils.find_sessionids_by_query(query=query, collection=ss.db_collection, limit=10)
    return ss.latest_sessionids


def main_inspect():
    cfg: Config = ss.cfg
    if "db_utils" not in ss:
        ss.db_utils = DBUtils()
    db_utils: DBUtils = ss.db_utils

    with st.sidebar:
        # 1. select `db_collection`
        col1, col2 = st.columns([1, 1])
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
            st.selectbox(
                "exp_version",
                options=cfg.db_available_exp_versions + [""],
                index=-1
                if cfg.st_default_exp_version not in cfg.db_available_exp_versions
                else cfg.db_available_exp_versions.index(cfg.st_default_exp_version),
                key="exp_version",
                on_change=lambda: get_latest_sessionids(refresh=True),
            )

        # 2. select speicific `session_id`
        col1, col2 = st.columns([1, 1])
        with col1:
            get_latest_sessionids()
            session_id = st.selectbox(
                "2️⃣ Select session_id",
                options=ss.latest_sessionids,
            )
            st.button("Refresh", on_click=lambda: get_latest_sessionids(refresh=True))
        with col2:
            customized_session_id = st.text_input("Or input a customized session_id:")
            if customized_session_id:
                session_id = customized_session_id
            display_option = st.selectbox(
                "Choose display option",
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
        st.info(f"- selected session_id: {session_id}")
