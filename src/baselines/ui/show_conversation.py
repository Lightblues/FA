import streamlit as st
import pandas as pd
from ..data import DBManager, Config, DataManager


def show_conversation_page():
    """
    Streamlit UI for baseline experiment.

    1. select a conversation_id from the sidebar
    2. display the conversation in the main window
    3. select an utterance_id from the main window
    4. display the details of the selected utterance_id in the main window

    st.session_state:
        - cfg: Config object
        - db: DBManager object
        - conversation_ids: list of conversation_ids

    Parameters
    ----------
    cfg_name : str
        the name of the configuration file
    """
    # ------------------ session_state --------------------
    if "db" not in st.session_state:
        assert 'cfg' in st.session_state
        cfg: Config = st.session_state.cfg
        st.session_state.db = DBManager(cfg.db_uri, cfg.db_name, cfg.db_message_collection_name)
    if "conversation_ids" not in st.session_state:
        st.session_state.conversation_ids = st.session_state.db.get_most_recent_unique_conversation_ids()
    db:DBManager = st.session_state.db
    
    # ------------------ sidebar --------------------
    # st.sidebar.title("Select Conversation")
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        conversation_id = st.selectbox("1️⃣ Select conversation_id (recent 10)", st.session_state.conversation_ids)
    with col2:
        if st.button("Refresh"):
            st.session_state.conversation_ids = db.get_most_recent_unique_conversation_ids()
    customized_conversation_id = st.sidebar.text_input(
        "Customized conversation_id"
    )
    if customized_conversation_id: conversation_id = customized_conversation_id
    st.sidebar.info(f"selected conversation_id: {conversation_id}")
    display_option = st.sidebar.selectbox(
        "Choose display option",
        ["Dataframe", "Table"]
    )

    # ------------------ main --------------------
    if conversation_id:
        # 1. query conversation from db ; show the conversation
        conv = db.query_messages_by_conversation_id(conversation_id)
        df = conv.to_dataframe()
        selected_columns = ['role', 'content', 'utterance_id']
        df_selected = df[selected_columns].set_index('utterance_id')
        st.markdown(f"### Conversation `{conversation_id}`")
        if display_option == "Dataframe":
            st.dataframe(df_selected)
        else:
            st.table(df_selected, ) # table is better for reading then st.dataframe!
        
        # 2. query config from db; show the config
        conversation_metas = db.query_config_by_conversation_id(conversation_id)
        st.markdown(f"### Configuration")
        with st.expander("Details"):
            st.write(conversation_metas)
        
        # 3. 创建一个下拉菜单来选择 utterance_id, 展示所选 utterance_id 的完整信息
        utterance_ids = df['utterance_id'].unique()
        selected_utterance_id = st.sidebar.selectbox("2️⃣ Select utterance_id", utterance_ids, placeholder="Select an utterance_id")
    
        st.markdown(f"### Details of `utterance_id={selected_utterance_id}`")
        with st.expander("Details"):
            if selected_utterance_id is not None:
                selected_row = df[df['utterance_id'] == selected_utterance_id].iloc[0]
                st.write(selected_row.to_dict())

