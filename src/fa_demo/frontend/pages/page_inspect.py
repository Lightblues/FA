"""
Inspect the history conversations.

Display logic:
1. select mode: single or multi;
2. select conversation_id, then show conversation and config;
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


cfg: Config = ss.cfg
COLLECTION_NAMES = {
    "single": cfg.db_collection_single,
    "multi": cfg.db_collection_multi,
}


def get_latest_sessionids(refresh: bool = False) -> List[str]:
    """set ss.latest_sessionids.
    NOTE: set refresh=True when ``ss.inspect_mode`` changes

    Args:
        refresh (bool, optional): weather to refresh cache_data. Defaults to False.
    """
    if ("latest_sessionids" not in ss) or refresh:
        db_utils: DBUtils = ss.db_utils
        ss.latest_sessionids = db_utils.get_latest_sessionids(n=10, collection=COLLECTION_NAMES[ss.inspect_mode])
    return ss.latest_sessionids


def main_inspect():
    if "db_utils" not in ss:
        ss.db_utils = DBUtils()
    # if "inspect_mode" not in ss: ss.inspect_mode = "single"  # NOTE: set default mode to single
    db_utils: DBUtils = ss.db_utils

    with st.sidebar:
        # 1. select interested mode
        st.selectbox(
            "1️⃣ Select mode",
            options=["single", "multi"],
            index=1,
            key="inspect_mode",
            on_change=lambda: get_latest_sessionids(refresh=True),
        )

        # 2. select speicific `conversation_id`
        col1, col2 = st.columns([3, 1])
        with col1:
            get_latest_sessionids()
            conversation_id = st.selectbox(
                "2️⃣ Select conversation_id",
                options=ss.latest_sessionids,
            )
        with col2:
            st.button("Refresh", on_click=lambda: get_latest_sessionids(refresh=True))
        customized_conversation_id = st.text_input("Or input a customized conversation_id:")
        if customized_conversation_id:
            conversation_id = customized_conversation_id
        st.info(f"selected conversation_id: {conversation_id}")
        display_option = st.selectbox(
            "Choose display option",
            options=["Table", "Dataframe"],
        )

    # ------------------ main --------------------
    if conversation_id:
        # 1. query conversation from db ; show the conversation
        cfg, conv = db_utils.get_data_by_sessionid(conversation_id, collection=COLLECTION_NAMES[ss.inspect_mode])
        if len(conv.msgs) == 0:
            st.warning(f"Conversation `{conversation_id}` is empty.")
            return
        df = conv.to_dataframe()
        selected_columns = ["role", "content", "utterance_id"]
        df_selected = df[selected_columns].set_index("utterance_id")
        st.markdown(f"### Conversation `{conversation_id}`")
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
