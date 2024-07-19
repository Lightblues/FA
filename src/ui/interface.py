""" 
> streamlit run run_ui.py

@240718 实现基本交互界面
- [ ] [optimize] optimize API output! 
- [x] [feat] show Huabu meta information in the sidebar
- [ ] [log] add more detailed logs
- [x] [feat] mofigy template/PDL in the web directly!  -- not good
"""

import time, os, json, glob, openai, yaml, datetime, pdb
import streamlit as st
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from .ui import init_page, init_sidebar
from .datamodel import init_agents, init_resource
from engine_v1.datamodel import (
    PDL, Role, Message, Conversation, ActionType, ConversationInfos, Logger, BaseLogger, BaseUser
)
from .bots import PDL_UIBot



def main():
    init_page()
    init_resource()
    init_sidebar()      # add configs!!!
    # cfg = Config.from_yaml(yaml_file="./ui/configs/default.yaml")
    init_agents()
    
    # TODO: print the header information
    # s_infos = "\n".join([f"{k}: {v}" for k, v in infos.to_dict().items()]) + "\n"
    # infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
    # self.logger.log(infos_header, with_print=True)

    # the main loop
    if 'conversation' not in st.session_state:
        st.session_state.conversation = Conversation()
    if 'conversation_infos' not in st.session_state:
        st.session_state.conversation_infos = ConversationInfos.from_components(
            previous_action_type=ActionType.START, num_user_query=0
        )
    conversation: Conversation = st.session_state.conversation
    conversation_infos: ConversationInfos = st.session_state.conversation_infos
    logger: BaseLogger = st.session_state.logger
    bot:PDL_UIBot = st.session_state.bot

    for message in conversation.msgs:
        if message.text.startswith("<"): continue  # NOTE: skip the API calling message
        with st.chat_message(message.role.rolename, avatar=st.session_state['avatars'][message.role.rolename]):
            st.write(message.text)

    # pdb.set_trace()
    if OBJECTIVE := st.chat_input('Input...'):       # NOTE: initial input!
        conversation.add_message(Message(Role.USER, OBJECTIVE))
        conversation_infos.previous_action_type = ActionType.USER
        with st.chat_message("user", avatar=st.session_state['avatars']['user']):
            st.write(OBJECTIVE)
        logger.log_to_stdout(f"[USER] {OBJECTIVE}")

        with st.container():
            while conversation_infos.previous_action_type in [ActionType.API, ActionType.USER]:    # If previous action is API, then call bot again
                prompt, llm_response_stream = bot.process_stream(conversation, conversation_infos)
                with st.expander(f"Thinking...", expanded=False):
                    llm_response = st.write_stream(llm_response_stream)
                _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<prompt>>\n{prompt}\n\n<<response>>\n{llm_response}\n"
                logger.debug(_debug_msg)
                parsed_response = Formater.parse_llm_output_json(llm_response)
                action_type = bot.process_LLM_response(conversation, parsed_response)       # messages added into conversation! 
                conversation_infos.previous_action_type = action_type
                # show API response to screen
                if action_type == ActionType.API:
                    with st.chat_message("system", avatar=st.session_state['avatars']['system']):
                        st.write(f"{conversation.msgs[-2].text}")
                        st.write(f"{conversation.msgs[-1].text}")
        with st.chat_message("assistant", avatar=st.session_state['avatars']['assistant']):
            st.write(conversation.msgs[-1].text)

