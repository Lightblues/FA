""" 
cases: https://doc.weixin.qq.com/sheet/e3_AcMATAZtAPIaxl2WshdR0KQkIBZdF?scode=AJEAIQdfAAoAaaG6YXAcMATAZtAPI&tab=BB08J2

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
@241204
- [x] #feat add tools for main agent (Google Search)
- [x] #feat #robust add error handler -> add retry_wrapper for `step_agent_main_prediction`
- [x] #feat #debug add Mocked LLM (model_name="debug")

- [ ] testing (debug): inspect prompt and output
- [ ] #bug, repeatly SWITCH workflow
- [ ] #doc add standard test cases in doc [cases]
- [ ] #feat #log save session infos with sessionid in db
"""
import streamlit as st; ss = st.session_state
import json
from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .ui_multi import init_sidebar, post_sidebar
from .data_multi import refresh_main_agent, refresh_workflow_agent, init_tools, db_upsert_session
from .page_single_workflow import step_user_input
from .bot_multi_main import Multi_Main_UIBot, MainBotOutput
from .bot_multi_workflow import Multi_Workflow_UIBot, WorkflowBotOutput
from .tool_llm import LLM_UITool
from ..tools import execute_tool_call
from ..utils import retry_wrapper



def step_api_process(agent_workflow_output: BotOutput) -> APIOutput:
    curr_tool: LLM_UITool = ss.curr_tool
    api_output = curr_tool.process(agent_workflow_output)        # add message! 
    st.markdown(f'<p style="color: green;">[API call] Got <code>{api_output.response_data}</code> from <code>{api_output.request}</code></p>', unsafe_allow_html=True)
    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return api_output

@retry_wrapper(retry=3, step_name="step_agent_main_prediction", log_fn=ss.logger.bind(custom=True).error)
def step_agent_main_prediction() -> MainBotOutput:
    agent_main: Multi_Main_UIBot = ss.agent_main
    print(f">> conversation: {json.dumps(str(ss.conv), ensure_ascii=False)}")
    prompt, stream = agent_main.process_stream()
    with st.expander(f"Thinking...", expanded=True):
        llm_response = st.write_stream(stream)
    agent_main_output: MainBotOutput = agent_main.process_LLM_response(prompt, llm_response)
    _debug_msg = f"\n{'[BOT]'.center(50, '=')}\nllm {agent_main.llm.model_name}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
    ss.logger.bind(custom=True).debug(_debug_msg)
    return agent_main_output

@retry_wrapper(retry=3, step_name="step_agent_workflow_prediction", log_fn=ss.logger.bind(custom=True).error)
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

def step_tool(agent_main_output: MainBotOutput):
    # see @ian /cq8/ianxxu/chatchat/_TaskPlan/UI/v2.1/IanAGI.py 
    tool_name, tool_args = agent_main_output.action, agent_main_output.action_input
    if tool_name in ("web_search"):
        spinner_info = f"Searching for {tool_args['query']}..."
    else: raise NotImplementedError
    with st.spinner(f"{ss['tool_emoji'][tool_name]} {spinner_info}"):
        # execute!
        res = execute_tool_call(tool_name, tool_args)
        msg = Message(
            "tool", res, 
            conversation_id=ss.conv.conversation_id, utterance_id=ss.conv.current_utterance_id
        )
        ss.conv.add_message(msg)
    if tool_name in ("web_search"):
        with st.expander(f"{ss['tool_emoji']['web_logo']} Searching results for '{tool_args['query']}'", expanded=False):
            st.write(res)
    else: raise NotImplementedError

def case_main():
    print(f"> entering case_main `{ss.curr_status}`")
    with st.container():
        for num_bot_actions in range(3):
            agent_main_output = step_agent_main_prediction()
            # print(f"> agent_main_output: {agent_main_output}")
            if agent_main_output.workflow:
                # show SWITCH
                st.markdown(f'<p style="color: blue;">[switch workflow] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
                ss.logger.info(ss.conv.get_last_message().to_str())
                break
            else:
                if agent_main_output.action:
                    tool_output = step_tool(agent_main_output)
                elif agent_main_output.response:
                    ss.logger.info(ss.conv.get_last_message().to_str())
                    break
                else: raise NotImplementedError
        else:
            pass
    # out of this container! 
    if agent_main_output.workflow:
        ss.curr_status = agent_main_output.workflow
        case_workflow()
    # save to db
    db_upsert_session()

def case_workflow():
    """ Workflow agent: 
    1) setup the agent; 
    2) loop:
        bot prediction
    """
    print(f"> entering case_workflow `{ss.curr_status}`")
    refresh_workflow_agent()
    with st.container():
        for num_bot_actions in range(ss.cfg.bot_action_limit):
            agent_workflow_output = step_agent_workflow_prediction()
            print(f"> agent_workflow_output: {agent_workflow_output}")
            if agent_workflow_output.workflow:
                st.markdown(f'<p style="color: blue;">[switch workflow] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
                ss.logger.info(ss.conv.get_last_message().to_str())
                break
            else:
                if agent_workflow_output.action:
                    if not _post_control(agent_workflow_output):
                        ss.logger.warning(ss.conv.get_last_message().to_str())
                        st.markdown(f'<p style="color: red;">[controller error] <code>{ss.conv.get_last_message().to_str()}</code></p>', unsafe_allow_html=True)
                        continue
                    api_output = step_api_process(agent_workflow_output)
                elif agent_workflow_output.response:
                    ss.logger.info(ss.conv.get_last_message().to_str())
                    if not (agent_workflow_output.action or agent_workflow_output.workflow):
                        break
                else: raise NotImplementedError
        else:
            pass
    if agent_workflow_output.workflow:
        ss.curr_status = "main"
        case_main()
    # save to db
    db_upsert_session()

def show_conversations(conversation: Conversation):
    for message in conversation.msgs:
        if not (message.role.rolename == "user" or message.role.rolename.startswith("bot")): continue
        elif (message.content.startswith("<")): continue
        with st.chat_message(message.role.rolename, avatar=ss['avatars'][message.role.rolename]):
            st.write(message.content)

def main_multi():
    """Main loop! see [~ui_conv.md]"""
    if "workflow_infos" not in ss:
        ss.workflow_infos = ss.data_manager.workflow_infos.values()
        if ss.cfg.mui_available_workflows:
            workflow_names = [w['name'] for w in ss.workflow_infos]
            assert all(w in workflow_names for w in ss.cfg.mui_available_workflows)
            ss.workflow_infos = [w for w in ss.workflow_infos if w['name'] in ss.cfg.mui_available_workflows]
        for w in ss.workflow_infos:
            w['is_activated'] = True
    init_tools()

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
