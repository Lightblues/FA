import streamlit as st
from ..data import Config

def init_sidebar():
    """Init the sidebar of multi workflow
    TODO: select used workflows
    """
    config: Config = st.session_state.config
