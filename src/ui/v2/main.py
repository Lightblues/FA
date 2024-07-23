""" 
> streamlit run run_ui.py --server.port 8501
url: http://agent-pdl.woa.com

@240718 实现基本交互界面
- [ ] [optimize] optimize API output! 
- [x] [feat] show Huabu meta information in the sidebar
- [ ] [log] add more detailed logs
- [x] [feat] mofigy template/PDL in the web directly!  -- not good
@240723 完成V2版本的UI
- [ ] [feat] clearily log and print infos
"""

import time, os, json, glob, openai, yaml, datetime, pdb, copy
import streamlit as st
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from .ui import init_page, init_sidebar
from .data import init_agents, init_resource
from .bot import PDL_UIBot
from engine_v2 import (
    Role, Message, Conversation, ConversationInfos, ActionType, Logger, PDL, PDLController, 
    ConversationController, BaseRole, V01APIHandler
)



def main():
    # 1] init
    init_page()
    init_resource()
    init_sidebar()      # add configs!!!
    init_agents()
    
    # TODO: print the header information
    # s_infos = "\n".join([f"{k}: {v}" for k, v in infos.to_dict().items()]) + "\n"
    # infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
    # self.logger.log(infos_header, with_print=True)

    # 2] prepare for session conversation
    if 'conversation' not in st.session_state:
        st.session_state.conversation = Conversation()
    if 'conversation_infos' not in st.session_state:
        st.session_state.conversation_infos = ConversationInfos.from_components(
            previous_action_type=ActionType.START, num_user_query=0
        )
    conversation: Conversation = st.session_state.conversation
    conversation_infos: ConversationInfos = st.session_state.conversation_infos
    logger: Logger = st.session_state.logger
    bot: PDL_UIBot = st.session_state.bot
    api: V01APIHandler = st.session_state.api_handler
    pdl: PDL = st.session_state.pdl
    pdl_controller: PDLController = st.session_state.pdl_controller
    curr_role, curr_action_type = Role.USER, ActionType.USER
    action_metas = None

    for message in conversation.msgs:
        if (message.role == Role.SYSTEM) or (message.content.startswith("<")):
            # NOTE: skip the API calling message!
            continue  
        with st.chat_message(message.role.rolename, avatar=st.session_state['avatars'][message.role.rolename]):
            st.write(message.content)

    # 3] the main loop!
    """ 
    交互逻辑: 
        当用户输入query之后, 用一个while循环来执行ANSWER或者API调用:
            用一个 expander 来展示stream输出
            若为API调用, 则进一步展示中间结果
        最后, 统一展示给用户的回复
        NOTE: 用 container 包裹的部分会在下一轮 query 后被覆盖
    """
    if OBJECTIVE := st.chat_input('Input...'):       # NOTE: initial input!
        # 3.1] user input
        conversation.add_message(Message(Role.USER, OBJECTIVE))
        conversation_infos.previous_action_type = ActionType.USER
        with st.chat_message("user", avatar=st.session_state['avatars']['user']):
            st.write(OBJECTIVE)
        # logger.log_to_stdout(f"[USER] {OBJECTIVE}")

        print(f"  <debug> conversation: {json.dumps(str(conversation), ensure_ascii=False)}")
        # 3.2] loop for bot response!
        with st.container():
            while True:
                # 1) get next role
                next_role = ConversationController.next_role(curr_role, curr_action_type)
                # 2) role processing, responding to the next role
                if next_role == Role.USER: break
                elif next_role == Role.BOT:
                    _conversation = copy.deepcopy(conversation)
                    for bot_prediction_steps in range(3):      # cfg.bot_prediction_steps_limit
                        # [CHANGE01]: 修改为 stream 的方式
                        prompt, llm_response_stream = bot.process_stream(conversation, pdl, conversation_infos)
                        with st.expander(f"Thinking...", expanded=False):
                            llm_response = st.write_stream(llm_response_stream)
                        parsed_response = Formater.parse_llm_output_json(llm_response)
                        action_type, action_metas, msg = bot.process_LLM_response(parsed_response)
                        # _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<prompt>>\n{action_metas['prompt']}\n\n<<response>>\n{action_metas['llm_response']}\n"
                        # logger.debug(_debug_msg)
                        
                        if action_type == ActionType.API:
                            check_pass, sys_msg_str = pdl_controller.check_validation(next_node=action_metas["action_name"])       # next_node
                            logger.log_to_stdout(f"  <controller> {msg.content}", color="gray")
                            logger.log_to_stdout(f"  <controller> {sys_msg_str}", color="gray")
                            if check_pass: break
                            else:
                                # FIXME: 这里有问题吗? 
                                _conversation.add_message(msg)
                                _conversation.add_message(Message(Role.SYSTEM, sys_msg_str))
                        else: break
                    else:
                        pass         # TODO: 增加兜底策略
                elif next_role == Role.SYSTEM:
                    action_type, action_metas, msg = api.process(conversation=conversation, paras=action_metas)
                else:
                    raise ValueError(f"Unknown role: {next_role}")
                # 3) update
                curr_role, curr_action_type = next_role, action_type
                conversation_infos.previous_action_type = curr_action_type
                conversation.add_message(msg)           # add msg universally
                # logger.log(msg.to_str(), with_print=False)

                # # show API response to screen
                # if action_type == ActionType.API:
                #     with st.chat_message("system", avatar=st.session_state['avatars']['system']):
                #         st.write(f"{conversation.msgs[-2].content}")
                #         st.write(f"{conversation.msgs[-1].content}")
        
        with st.chat_message("assistant", avatar=st.session_state['avatars']['assistant']):
            st.write(conversation.msgs[-1].content)

