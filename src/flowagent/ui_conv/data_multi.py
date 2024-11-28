import datetime, copy, json
import streamlit as st; ss = st.session_state
from ..data import Conversation, Message, Role, Config, Workflow
from ..pdl_controllers import CONTROLLER_NAME2CLASS, BaseController
from .bot_multi_main import Multi_Main_UIBot
from .bot_multi_workflow import Multi_Workflow_UIBot
from .tool_llm import LLM_UITool
from .data_single import get_workflow_names_map

def debug_print_infos() -> None:
    print(f"[DEBUG] Conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    print(f"  > cfg: {ss.cfg}")
    print(f"  > curr_status: {ss.curr_status}")

def refresh_conversation() -> Conversation:
    """Init or refresh the conversation"""
    print(f">> Refreshing conversation!")
    if "conv" not in ss: ss.conv = Conversation()
    else:
        ss.conv.clear()
        ss.conv.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    msg_hello = Message(
        "bot_main", "你好，有什么可以帮您?", 
        conversation_id=ss.conv.conversation_id, utterance_id=ss.conv.current_utterance_id)
    ss.conv.add_message(msg_hello)
    
    ss.curr_workflow = "main"  # also reset the status!
    return ss.conv

def refresh_main_agent() -> Multi_Main_UIBot:
    """refresh the main agent: 1) reset ss.conv; 2) update ss.cfg; 3) init ss.agent_main
    """
    print(f">> Refreshing main agent:")
    refresh_conversation()
    
    cfg:Config = ss.cfg  # update ss.cfg will also update ss.bot
    cfg.mui_agent_main_llm_name = ss.selected_mui_agent_main_llm_name
    cfg.mui_agent_main_template_fn = f"flowagent/{ss.selected_mui_agent_main_template_fn}"
    
    if 'agent_main' not in ss:
        ss.agent_main = Multi_Main_UIBot()
    else:
        # update 
        ss.agent_main.refresh_config()
    return ss.agent_main

def refresh_workflow_agent() -> None:
    """refresh the specific workflow bot (ss.curr_status)
    """
    print(f">> Refreshing bot: `{ss.curr_status}`")
    # refresh_conversation()
    
    if ss.curr_status in ss.agent_workflow_map:
        ss.curr_workflow, ss.curr_bot, ss.curr_tool, ss.curr_controllers = ss.agent_workflow_map[ss.curr_status]
        print(f"> use cached workflow agent {ss.curr_bot}!")
    else:
        _, name_id_map = get_workflow_names_map()
        cfg:Config = copy.deepcopy(ss.cfg)  # update ss.cfg will also update ss.bot?
        cfg.bot_template_fn = f"flowagent/{ss.selected_mui_workflow_main_template_fn}"
        cfg.bot_llm_name = ss.selected_mui_agent_workflow_llm_name
        cfg.workflow_id = name_id_map['PDL_zh'][ss.curr_status]
        
        # setup workflow, bot, tool
        # if workflow_name not in 
        ss.curr_workflow = Workflow(cfg) # TODO: refresh workflow
        ss.curr_bot = Multi_Workflow_UIBot()
        ss.curr_tool = LLM_UITool()
        ss.curr_controllers = {}  # {name: BaseController}
        for c in ss.cfg.bot_pdl_controllers:
            ss.curr_controllers[c['name']] = CONTROLLER_NAME2CLASS[c['name']](ss.conv, ss.curr_workflow.pdl, c['config'])
        print(f"> created a new workflow agent {ss.curr_bot}!")
    return
