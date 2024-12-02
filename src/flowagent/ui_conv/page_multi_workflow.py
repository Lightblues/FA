""" 
@241125 implement main agent (step 1)
- [x] main agent
- [x] seperate single and multi workflow logic (refactor)
@241126
- [x] implement workflow agents
- [x] limit # ActionType.SWITCH in single turn (to avoid dead loop)? Maybe not necessary
@241127
- [x] add activated workflow in the sidebar (ui_multi.py)
@241202
- [x] #bug, cannot refresh ss.conv when changing Single/Multi
- [x] #feat refresh main & all workflow agents in [UI]
- [x] #feat select workflow_dataset in [UI]


- [ ] add tools for main agent (function calling?)
- [ ] testing (debug): inspect prompt and output
- [ ] #bug, repeatly SWITCH workflow
"""
import streamlit as st; ss = st.session_state
import json
from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .ui_multi import init_sidebar, post_sidebar
from .data_multi import refresh_conversation, refresh_main_agent, refresh_workflow_agent
from .page_single_workflow import show_conversations, step_user_input
from .bot_multi_main import Multi_Main_UIBot, MainBotOutput
from .bot_multi_workflow import Multi_Workflow_UIBot, WorkflowBotOutput
from .tool_llm import LLM_UITool



def step_api_process(agent_workflow_output: BotOutput) -> APIOutput:
    curr_tool: LLM_UITool = ss.curr_tool
    api_output = curr_tool.process(agent_workflow_output)        # add message! 
    st.markdown(f'<p style="color: green;">[API call] Got <code>{api_output.response_data}</code> from <code>{api_output.request}</code></p>', unsafe_allow_html=True)
    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return api_output


def step_agent_main_prediction() -> MainBotOutput:
    agent_main: Multi_Main_UIBot = ss.agent_main
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    prompt, stream = agent_main.process_stream()
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(stream)
    agent_main_output: MainBotOutput = agent_main.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\nllm {agent_main.llm.model_name}\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return agent_main_output

def step_agent_workflow_prediction() -> WorkflowBotOutput:
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    curr_bot: Multi_Workflow_UIBot = ss.curr_bot
    prompt, stream = curr_bot.process_stream()
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(stream)
    agent_workflow_output: WorkflowBotOutput = curr_bot.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\nllm {curr_bot.llm.model_name}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return agent_workflow_output

def _post_control(bot_output: BotOutput, ) -> bool:
    """ Check the validation of bot's action
    NOTE: if not validated, the error infomation will be added to ss.conv!
    """
    for controller in ss.curr_controllers.values():
        if not controller.if_post_control: continue
        if not controller.post_control(bot_output): return False
    return True

def case_main():
    print(f"> entering case_main `{ss.curr_status}`")
    with st.container():
        agent_main_output = step_agent_main_prediction()
        print(f"> agent_main_output: {agent_main_output}")
        if agent_main_output.action_type == BotOutputType.SWITCH:
            # show SWITCH
            st.markdown(f'<p style="color: blue;">[switch workflow] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
            ss.logger.info(ss.conv.get_last_message().to_str())
    # out of this container! 
    if agent_main_output.workflow:
        ss.curr_status = agent_main_output.workflow
        case_workflow()

def case_workflow():
    """ Workflow agent: 
    1) setup the agent; 
    2) loop:
        bot prediction
    """
    print(f"> entering case_workflow `{ss.curr_status}`")
    num_bot_actions = 0
    refresh_workflow_agent()
    with st.container():
        while True:
            agent_workflow_output = step_agent_workflow_prediction()
            print(f"> agent_workflow_output: {agent_workflow_output}")
            if agent_workflow_output.response:
                ss.logger.info(ss.conv.get_last_message().to_str())
                if not (agent_workflow_output.action or agent_workflow_output.workflow):
                    break
            if agent_workflow_output.action:
                if not _post_control(agent_workflow_output):
                    ss.logger.warning(ss.conv.get_last_message().to_str())
                    st.markdown(f'<p style="color: red;">[controller error] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
                    continue
                api_output = step_api_process(agent_workflow_output)
            elif agent_workflow_output.workflow:
                st.markdown(f'<p style="color: blue;">[switch workflow] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
                ss.logger.info(ss.conv.get_last_message().to_str())
                break
            # else: raise TypeError(f"Unexpected agent_workflow_output: {agent_workflow_output}")
            
            num_bot_actions += 1
            if num_bot_actions > ss.cfg.bot_action_limit: 
                break
    if agent_workflow_output.workflow:
        ss.curr_status = "main"
        case_main()

def main_multi():
    """Main loop! see [~ui_conv.md]"""
    if "logger" not in ss: ss.logger = init_loguru_logger(DataManager.DIR_ui_log)
    if "workflow_infos" not in ss:
        ss.workflow_infos = ss.data_manager.workflow_infos.values()
        if ss.cfg.mui_available_workflows:
            workflow_names = [w['name'] for w in ss.workflow_infos]
            assert all(w in workflow_names for w in ss.cfg.mui_available_workflows)
            ss.workflow_infos = [w for w in ss.workflow_infos if w['name'] in ss.cfg.mui_available_workflows]
        for w in ss.workflow_infos:
            w['is_activated'] = True

    init_sidebar()
    if ("mode" not in ss) or (ss.mode == "single"):
        # init agent_main when session start
        ss.mode = "multi"
        refresh_main_agent()
        ss.curr_status = "main"
        ss.agent_workflow_map = {}  # {name: (bot, tool)}
    
    post_sidebar()
    
    show_conversations(ss.conv)
    if OBJECTIVE := st.chat_input('Input...'):
        step_user_input(OBJECTIVE)
        if ss.curr_status == "main": case_main()
        else: case_workflow()

        with st.chat_message("assistant", avatar=ss['avatars']['assistant']):
            st.write(ss.conv.get_last_message().content)
