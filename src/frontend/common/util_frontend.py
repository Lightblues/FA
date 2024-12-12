from typing import List, Dict, Iterator, Union
import time
import streamlit as st
from flowagent.data import APIOutput, Message

def fake_stream(response: str) -> Iterator[str]:
    for chunk in response:
        yield chunk
        time.sleep(0.002)

class StreamlitUtils:
    def show_api_call(self, api_output: APIOutput):
        content = f"[API call] Got <code>{api_output.response_data}</code> from <code>{self.decode_html(api_output.request)}</code>"
        st.markdown(f'<p style="color: green;">{content}</p>', unsafe_allow_html=True)

    def show_switch_workflow(self, msg: Union[str, Message]):
        st.markdown(f'<p style="color: blue;">[switch workflow] <code>{self.decode_html(msg)}</code></p>', unsafe_allow_html=True)

    def show_controller_error(self, msg: Union[str, Message]):
        st.markdown(f'<p style="color: red;">[controller error] <code>{self.decode_html(msg)}</code></p>', unsafe_allow_html=True)

    def decode_html(self, s) -> str:
        if not isinstance(s, str): s = str(s)
        return s.replace("<", "&lt;").replace(">", "&gt;")
