import streamlit as st; self = st.session_state
from ..data import Config

def init_sidebar():
    """Init the sidebar of multi workflow
    TODO: select used workflows
    """
    config: Config = self.cfg
