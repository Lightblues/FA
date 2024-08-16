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
"""

import time, os, json, glob, openai, yaml, datetime, pdb, copy, sys
import streamlit as st
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from .ui import init_page, init_sidebar
from .data import init, init_resource
from .bot import PDL_UIBot
from engine_v2 import (
    Role, Message, Conversation, ConversationInfos, ActionType, Logger, PDL, PDLController, 
    ConversationController, V01APIHandler, Config, DataManager
)

def set_global_exception_handler(f):
    script_runner = sys.modules["streamlit.runtime.scriptrunner.script_runner"]
    script_runner.handle_uncaught_app_exception.__code__ = f.__code__

def exception_handler(e):
    import traceback
    # Custom error handling
    st.image("https://media1.tenor.com/m/t7_iTN0iYekAAAAd/sad-sad-cat.gif")
    print(traceback.format_exc())
    st.error(f"Oops, something funny happened with a {type(e).__name__}", icon="😿")

set_global_exception_handler(exception_handler)


def main(config_version:str="default.yaml"):
    # 1] init
    if "config" not in st.session_state:
        st.session_state.config = Config.from_yaml(DataManager.normalize_config_name(config_name=config_version))
        print(f"[INFO] config: {st.session_state.config}")
    init_page()
    init_resource()     # data: avatars, tool_emoji
    init_sidebar()      # data: DICT_workflow_info, user_additional_constraints, model_name, template_fn, workflow_dir, workflow_name
        # pdl, pdl_controller
    init()              # data: api_handler, 
        # refresh: config, bot, (workflow_name, workflow_dir)
        # refresh_conversation: conversation, conversation_infos, logger
    
    # 2] prepare for session conversation
    config: Config = st.session_state.config
    conversation: Conversation = st.session_state.conversation
    conversation_infos: ConversationInfos = st.session_state.conversation_infos
    logger: Logger = st.session_state.logger
    bot: PDL_UIBot = st.session_state.bot
    api: V01APIHandler = st.session_state.api_handler
    pdl: PDL = st.session_state.pdl
    pdl_controller: PDLController = st.session_state.pdl_controller
    
    # curr_role, curr_action_type    # init!!! move to conversation_infos
    action_metas = None

    for message in conversation.msgs:
        if (message.role == Role.SYSTEM) or (message.content.startswith("<")):
            # NOTE: skip the API calling message!
            continue  
        with st.chat_message(message.role.rolename, avatar=st.session_state['avatars'][message.role.rolename]):
            st.write(message.content)

    # _with_print = True
    _with_print = False
    # if conversation_infos.curr_action_type == ActionType.START:   # NOTE: 仍然为导致输出两遍!!
    if logger.num_logs == 0:
        logger.log(f"{'config'.center(50, '=')}\n{config.to_str()}\n{'-'*50}", with_print=_with_print)
        logger.log(f"available apis: {api.api_infos_map.keys()}\n{'-'*50}", with_print=_with_print)
        logger.log(conversation.msgs[0].to_str(), with_print=_with_print)

    # 3] the main loop!
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
    if OBJECTIVE := st.chat_input('Input...'):       # NOTE: initial input!
        # 3.1] user input
        msg_user = Message(Role.USER, OBJECTIVE)
        conversation.add_message(msg_user)
        conversation_infos.curr_role = Role.USER
        conversation_infos.curr_action_type = ActionType.USER_INPUT
        with st.chat_message("user", avatar=st.session_state['avatars']['user']):
            st.write(OBJECTIVE)
        logger.log(f"{msg_user.to_str()}", with_print=_with_print)

        print(f">> conversation: {json.dumps(str(conversation), ensure_ascii=False)}")
        # 3.2] loop for bot response!
        with st.container():
            while True:
                # 1) get next role
                # print(f">> conversation_infos: {json.dumps(str(conversation_infos), ensure_ascii=False)}")
                next_role = ConversationController.next_role(conversation_infos.curr_role, conversation_infos.curr_action_type)
                # 2) role processing, responding to the next role
                if next_role == Role.USER: break
                elif next_role == Role.BOT:
                    _conversation = copy.deepcopy(conversation)     # tmp 变量
                    for bot_prediction_steps in range(3):      # cfg.bot_prediction_steps_limit
                        # [CHANGE01]: 修改为 stream 的方式
                        prompt, llm_response_stream = bot.process_stream(conversation, pdl, conversation_infos)
                        with st.expander(f"Thinking...", expanded=True):
                            llm_response = st.write_stream(llm_response_stream)
                        parsed_response = Formater.parse_llm_output_json(llm_response)
                        action_type, action_metas, msg = bot.process_LLM_response(parsed_response)
                        action_metas.update(prompt=prompt, llm_response=llm_response)       # NOTE: update the action_metas!!
                        _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<lllm prompt>>\n{action_metas['prompt']}\n\n<<llm response>>\n{action_metas['llm_response']}\n"
                        logger.debug(_debug_msg)
                        
                        if action_type == ActionType.API:
                            check_pass, sys_msg_str = pdl_controller.check_validation(next_node=action_metas["action_name"])       # next_node
                            msg_system = Message(Role.SYSTEM, sys_msg_str)
                            logger.log(f"  {msg.content}\n  {msg_system.content}", with_print=_with_print)
                            _debug_msg = f"{'[PDL_controller]'.center(50, '=')}\n<<requested api>>\n{msg.content}\n\n<<controller response>>\n{sys_msg_str}\n"
                            logger.debug(_debug_msg)
                            if check_pass: break
                            else:
                                # NOTE: 仅在中间过程记录错误调用的尝试! 
                                _conversation.add_message(msg)
                                _conversation.add_message(msg_system)
                                st.markdown(f'<p style="color: red;">[controller error] <code>{sys_msg_str}</code></p>', unsafe_allow_html=True)
                        else: break
                    else:
                        pass         # TODO: 增加兜底策略
                elif next_role == Role.SYSTEM:
                    action_type, action_metas, msg = api.process(conversation=conversation, paras=action_metas)
                    _debug_msg = f"{'[API]'.center(50, '=')}\n<<calling api>>\n{action_metas}\n\n<< api response>>\n{msg.content}\n"
                    logger.debug(_debug_msg)
                else:
                    raise ValueError(f"Unknown role: {next_role}")
                # 3) update
                conversation_infos.curr_role, conversation_infos.curr_action_type = next_role, action_type
                conversation.add_message(msg)           # add msg universally
                logger.log(msg.to_str(), with_print=_with_print)

                # show API response to screen
                if conversation_infos.curr_action_type == ActionType.API_RESPONSE:
                    st.markdown(f'<p style="color: green;">[API call] Got <code>{msg.content}</code> from <code>{conversation.msgs[-2].content}</code></p>', unsafe_allow_html=True)
        
        # [show] final bot response to screen
        with st.chat_message("assistant", avatar=st.session_state['avatars']['assistant']):
            st.write(conversation.msgs[-1].content)

