from loguru._logger import Logger
import streamlit as st; ss = st.session_state
import json
from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .ui_multi import init_sidebar
from .data_single import refresh_workflow
from .data_multi import refresh_conversation, refresh_main_agent
from .page_single_workflow import show_conversations, step_user_input
from .bot_multi_main import Multi_Main_UIBot, MainBotOutput

def step_bot_prediction() -> BotOutput:
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    prompt, stream = ss.bot.process_stream()
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(stream)
    bot_output: BotOutput = ss.bot.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return bot_output

def step_api_process(bot_output: BotOutput) -> APIOutput:
    api_output: APIOutput = ss.api_handler.process(bot_output)        # add message! 
    st.markdown(f'<p style="color: green;">[API call] Got <code>{api_output.response_data}</code> from <code>{api_output.request}</code></p>', unsafe_allow_html=True)
    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return api_output


def get_workflow_agent(workflow_name:str):
    """ Setup for each workflow
    global variables: bot / tool
    """
    if workflow_name in ss.agent_workflow_map:
        ss.bot, ss.tool = ss.agent_workflow_map[workflow_name]
    else:
        ss.bot, ss.tool = refresh_workflow(workflow_name)
        ss.agent_workflow_map[workflow_name] = (ss.bot, ss.tool)

def step_main_prediction() -> MainBotOutput:
    bot: Multi_Main_UIBot = ss.agent_main
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    prompt, stream = bot.process_stream()
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(stream)
    bot_output: MainBotOutput = bot.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return bot_output

def case_main():
    bot_output = step_main_prediction()
    if bot_output.workflow:
        ss.curr_workflow = "workflow"
        case_workflow()
def case_workflow():
    agent_workflow = get_workflow_agent(ss.curr_workflow)
    res = agent_workflow.process()
    if res.main:
        ss.status = "main"
        case_main()

def main_multi():
    """Main loop! see [~ui_conv.md]"""
    if "logger" not in ss: ss.logger = init_loguru_logger(DataManager.DIR_ui_log)
    if "conv" not in ss: ss.conv = refresh_conversation()
    if "curr_workflow" not in ss: ss.curr_workflow = "main"
    if "agent_main" not in ss: refresh_main_agent()
    if "agent_workflow_map" not in ss: ss.agent_workflow_map = {}  # {name: (bot, tool)}
    
    init_sidebar()
    
    show_conversations(ss.conv)
    if OBJECTIVE := st.chat_input('Input...'):
        step_user_input(OBJECTIVE)
        with st.container():
            if ss.curr_workflow == "main":
                case_main()
            else: case_workflow()

        with st.chat_message("assistant", avatar=ss['avatars']['assistant']):
            st.write(ss.conv.get_last_message().content)
