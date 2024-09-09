import streamlit as st
import pandas as pd
from ..data import DBManager, Config, DataManager



def main(cfg_name: str):
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
    if "cfg" not in st.session_state:
        cfg = Config.from_yaml(
            DataManager.normalize_config_name(cfg_name)
        )
        st.session_state.cfg = cfg
        st.session_state.db = DBManager(cfg.db_uri, cfg.db_name, cfg.db_message_collection_name)
        st.session_state.conversation_ids = st.session_state.db.get_most_recent_unique_conversation_ids()
    db:DBManager = st.session_state.db
    
    # st.sidebar.title("Select Conversation")
    col1, col2 = st.sidebar.columns([1, 3])
    with col1:
        if st.button("Refresh"):
            st.session_state.conversation_ids = db.get_most_recent_unique_conversation_ids()
    with col2:
        conversation_id = st.selectbox("Select conversation_id", st.session_state.conversation_ids)


    if conversation_id:
        # 1. query conversation from db
        conv = db.query_messages_by_conversation_id(conversation_id)
        df = conv.to_dataframe()
        selected_columns = ['role', 'content', 'utterance_id']
        df_selected = df[selected_columns].set_index('utterance_id')
        
        # 2. show the conversation
        st.markdown(f"### Conversation `{conversation_id}`")
        st.table(df_selected, ) # table is better for reading then st.dataframe!
        
        # 3. 创建一个下拉菜单来选择 utterance_id, 展示所选 utterance_id 的完整信息
        st.markdown(f"### Details of selected utterance_id")
        utterance_ids = df['utterance_id'].unique()
        selected_utterance_id = st.selectbox("Select utterance_id", utterance_ids, placeholder="Select an utterance_id")
        if selected_utterance_id is not None:
            selected_row = df[df['utterance_id'] == selected_utterance_id].iloc[0]
            st.write(selected_row.to_dict())
