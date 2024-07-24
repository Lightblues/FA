""" The main conversation controller!

@240718 抽象整体结构, 完成 ConversationController
"""

import os, sys, time, datetime, copy

from .datamodel import (
    Role, Message, Conversation, ActionType, ConversationInfos, Config
)
from .role_bot import PDLBot
from .role_user import InputUser, LLMSimulatedUserWithRefConversation
from .role_api import ManualAPIHandler, V01APIHandler
from .pdl import PDL
from .common import Logger
from .controller import PDLController


class ConversationController:
    cfg: Config = None
    user: InputUser = None
    bot: PDLBot = None
    api: V01APIHandler = None
    logger: Logger = None
    pdl_controller: PDLController = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.user = InputUser()
        self.bot = PDLBot(cfg=cfg)
        if cfg.api_mode == "manual":
            self.api = ManualAPIHandler()
        elif cfg.api_mode == "v01":
            self.api = V01APIHandler()  # paras: [fn_api_infos]
        else:
            raise ValueError(f"Unknown api_mode: {cfg.api_mode}")
        self.logger = Logger()
    
    @staticmethod
    def next_role(curr_role:Role, action_type:ActionType) -> Role:
        """ Logic for conversation control! """
        # 边界情况: START? 
        if action_type == ActionType.START:
            return Role.USER
        
        # 一般情况下的条件转移
        if curr_role in [Role.USER, Role.SYSTEM]:
            return Role.BOT
        elif curr_role == Role.BOT:
            if action_type in [ActionType.REQUEST, ActionType.ANSWER]:
                return Role.USER
            elif action_type == ActionType.API:
                return Role.SYSTEM
            else:
                raise ValueError(f"Unknown action_type: {action_type}")
        else:
            raise ValueError(f"Unknown role: {curr_role}")
        
    def conversation(self, pdl:PDL):
        """ 
        data for 3 roles:
            conversation/conversation_infos, pdl
        """
        # 0] init; add the hello message
        msg_hello = Message(Role.BOT, f"你好，我是{self.cfg.workflow_name}机器人，有什么可以帮您?")
        self.logger.log(msg_hello.to_str(), with_print=False)
        self.logger.log_to_stdout(msg_hello.to_str(), color=msg_hello.role.color)
        conversation = Conversation()
        conversation.add_message(msg_hello)
        conversation_infos = ConversationInfos.from_components(             # useful information for bot
            curr_role=Role.BOT, curr_action_type=ActionType.START, num_user_query=0
        )
        # curr_role, curr_action_type = Role.USER, ActionType.START
        action_metas = None
        
        # 1] the main loop: until get answer! (finish the PDL task)
        while conversation_infos.curr_action_type != ActionType.ANSWER:
            # 1.1] get next role
            next_role = self.next_role(conversation_infos.curr_role, conversation_infos.curr_action_type)
            # 1.2] role processing, responding to the next role
            if next_role == Role.USER:
                action_type, action_metas, msg = self.user.process(conversation=conversation)
                conversation_infos.num_user_query += 1
            elif next_role == Role.BOT:
                _conversation = copy.deepcopy(conversation)
                for bot_prediction_steps in range(3):      # cfg.bot_prediction_steps_limit
                    action_type, action_metas, msg = self.bot.process(
                        conversation=_conversation, pdl=pdl, conversation_infos=conversation_infos, 
                        print_stream=False          # cfg.bot_print_stream
                    )
                    _debug_msg = f"{'[BOT]'.center(50, '=')}\n<<prompt>>\n{action_metas['prompt']}\n\n<<response>>\n{action_metas['llm_response']}\n"
                    self.logger.debug(_debug_msg)
                    
                    if action_type == ActionType.API:
                        check_pass, sys_msg_str = self.pdl_controller.check_validation(next_node=action_metas["action_name"])       # next_node
                        self.logger.log_to_stdout(f"  <controller> {msg.content}", color="gray")
                        self.logger.log_to_stdout(f"  <controller> {sys_msg_str}", color="gray")
                        if check_pass: break
                        else:
                            # FIXME: 之类有问题吗? 
                            _conversation.add_message(msg)
                            _conversation.add_message(Message(Role.SYSTEM, sys_msg_str))
                    else: break
                else:
                    pass         # TODO: 增加兜底策略
            elif next_role == Role.SYSTEM:
                # TODO: add log for api??
                action_type, action_metas, msg = self.api.process(conversation=conversation, paras=action_metas)
            else:
                raise ValueError(f"Unknown role: {next_role}")
            # 1.3] update
            conversation_infos.curr_role = next_role
            conversation_infos.curr_action_type = action_type
            conversation.add_message(msg)           # add msg universally
            self.logger.log(msg.to_str(), with_print=False)
            if conversation_infos.curr_role not in [Role.USER]: self.logger.log_to_stdout(msg.to_str(), color=conversation_infos.curr_role.color)

        return conversation
    
    def start_conversation(self):
        # [1] workflow_name -> PDL
        pdl = PDL.load_from_file(f"{self.cfg.workflow_dir}/{self.cfg.workflow_name}.txt")
        self.pdl_controller = PDLController(pdl=pdl)
        
        # [2] print the header information
        t_now = datetime.datetime.now()
        infos = {
            # "workflow_name": self.cfg.workflow_name,
            # "model_name": self.cfg.model_name,
            # "template_fn": self.cfg.template_fn,
            # "workflow_dir": self.cfg.workflow_dir,
            "log_file": self.logger.log_fn,
            "time": t_now.strftime("%Y-%m-%d %H:%M:%S"),
            "config": self.cfg.to_dict(),
        }
        s_infos = "\n".join([f"{k}: {v}" for k, v in infos.items()]) + "\n"
        infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
        self.logger.log(infos_header, with_print=True)

        # [3] start! 
        conversation = self.conversation(pdl)

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)
        return infos, conversation
        