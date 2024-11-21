
""" 
> streamlit run run_ui.py --server.port 8501
url: http://agent-pdl.woa.com

@240718 实现基本交互界面
- [ ] [optimize] optimize API output! 
- [x] [feat] show Huabu meta information in the sidebar
- [x] [log] add more detailed logs
- [x] [feat] mofigy template/PDL in the web directly!  -- not good
@240723 完成V2版本的UI
- [x] [feat] clearily log and print infos

- [x] refactor: align with [~master]
"""

import time, os, json, glob, openai, yaml, datetime, pdb, copy, sys
from loguru._logger import Logger
import streamlit as st

from ..data import (
    DataManager, Config, Workflow, 
    Conversation, Message, Role, init_loguru_logger,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .ui_single import init_sidebar
from .ui_data import refresh_bot


def show_conversations(conversation):
    for message in conversation.msgs:
        if (message.role == Role.SYSTEM) or (message.content.startswith("<")):
            continue  
        with st.chat_message(message.role.rolename, avatar=st.session_state['avatars'][message.role.rolename]):
            st.write(message.content)

def main_single():
    # 1. init
    if "logger" not in st.session_state:
        st.session_state.logger = init_loguru_logger(DataManager.DIR_ui_log)
    if "workflow" not in st.session_state:
        st.session_state.workflow = Workflow(st.session_state.config)

    init_sidebar()

    if "bot" not in st.session_state:
        refresh_bot()
    # 2. prepare for session conversation
    config: Config = st.session_state.config
    conversation: Conversation = st.session_state.conversation
    logger: Logger = st.session_state.logger
    # workflow: Workflow = st.session_state.workflow

    # if logger.num_logs == 0:
    #     logger.info(f"{'config'.center(50, '=')}\n{config.to_dict()}\n{'-'*50}", with_print=_with_print)
    #     logger.info(f"available apis: {[t['name'] for t in workflow.toolbox]}\n{'-'*50}", with_print=_with_print)
    #     logger.info(conversation.msgs[0].to_str(), with_print=_with_print)

    # 3. the main loop!
    """ 
    交互逻辑: 
        当用户输入query之后, 用一个while循环来执行ANSWER或者API调用:
            用一个 expander 来展示stream输出
            若为API调用, 则进一步展示中间结果
        最后, 统一展示给用户的回复
        NOTE: 用 container 包裹的部分会在下一轮 query 后被覆盖
    日志:
        summary: 类似conversation交互, 可以增加必要信息
        detailed: 记录设计到LLM的详细信息
    """
    show_conversations(conversation)
    if OBJECTIVE := st.chat_input('Input...'):
        msg_user = Message(Role.USER, OBJECTIVE, conversation_id=conversation.conversation_id, utterance_id=conversation.current_utterance_id)
        conversation.add_message(msg_user)
        with st.chat_message("user", avatar=st.session_state['avatars']['user']):
            st.write(OBJECTIVE)
        logger.info(f"{msg_user.to_str()}")
        print(f">> conversation: {json.dumps(str(conversation), ensure_ascii=False)}")

        with st.container():
            num_bot_actions = 0
            while True:
                # 0. pre-control
                # self._pre_control(bot_output)
                # 1. bot predict an action
                prompt, stream = st.session_state.bot.process_stream()
                with st.expander(f"Thinking...", expanded=True):
                    llm_response = st.write_stream(stream)
                bot_output: BotOutput = st.session_state.bot.process_LLM_response(prompt, llm_response)
                _debug_msg = f"\n{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{prompt}\n\n<<llm response>>\n{llm_response}\n"
                logger.bind(custom=True).debug(_debug_msg)
                
                # 2. STOP: break until bot RESPONSE
                if bot_output.action_type == BotOutputType.END: break  # TODO: remove END for web version
                elif bot_output.action_type == BotOutputType.RESPONSE:
                    logger.info(conversation.get_last_message().to_str())
                    break
                elif bot_output.action_type == BotOutputType.ACTION:
                    # TODO: action control
                    # 3. ACTION loop: call the API, append results to conversation
                    # 3.1. post-check the action! (will be ignored for non-PDLBot)
                    # if not self._post_control(bot_output):
                    #     self.log_msg(self.conv.get_last_message(), verbose=verbose)  # log the error info!
                    #     continue
                    # _debug_msg = f"{'[PDL_controller]'.center(50, '=')}\n<<requested api>>\n{msg.content}\n\n<<controller response>>\n{sys_msg_str}\n"
                    # st.markdown(f'<p style="color: red;">[controller error] <code>{sys_msg_str}</code></p>', unsafe_allow_html=True)
                    # 3.2 call the API (system)
                    api_output: APIOutput = st.session_state.api_handler.process(bot_output)
                    st.markdown(f'<p style="color: green;">[API call] Got <code>{api_output.response_data}</code> from <code>{api_output.request}</code></p>', unsafe_allow_html=True)
                    _debug_msg = f"\n{'[API]'.center(50, '=')}\n<<calling api>>\n{api_output.request}\n\n<< api response>>\n{api_output.response_data}\n"
                    logger.bind(custom=True).debug(_debug_msg)
                else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
                
                num_bot_actions += 1
                if num_bot_actions > config.bot_action_limit: 
                    break
        
        # show final bot response to screen
        with st.chat_message("assistant", avatar=st.session_state['avatars']['assistant']):
            st.write(conversation.get_last_message().content)

        # DB
        # infos_dict = {
        #     "conversation_id": conversation.conversation_id, **config.to_dict()
        # }