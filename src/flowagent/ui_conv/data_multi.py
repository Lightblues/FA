import datetime
import streamlit as st; ss = st.session_state
from .bot_multi_main import Multi_Main_UIBot
from ..data import Conversation, Message, Role

def refresh_conversation() -> Conversation:
    """Init or refresh the conversation"""
    print(f">> Refreshing conversation!")
    if "conv" not in ss: ss.conv = Conversation()
    else:
        ss.conv.clear()
        ss.conv.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    msg_hello = Message(
        Role.BOT, "你好，有什么可以帮您?", 
        conversation_id=ss.conv.conversation_id, utterance_id=ss.conv.current_utterance_id)
    ss.conv.add_message(msg_hello)
    return ss.conv

def refresh_main_agent() -> Multi_Main_UIBot:
    """refresh the bot
    """
    print(f">> Refreshing main agent:") #  `{ss.selected_template_fn}`
    conv = refresh_conversation()
    
    # cfg:Config = ss.cfg  # update ss.cfg will also update ss.bot?
    # cfg.bot_template_fn = f"flowagent/{ss.selected_template_fn}"
    # cfg.bot_llm_name = ss.selected_model_name
    
    if 'agent_main' not in ss:
        ss.agent_main = Multi_Main_UIBot()
    else:
        ss.agent_main.refresh_config()