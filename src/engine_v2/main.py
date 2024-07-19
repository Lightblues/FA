

import os, sys, time, datetime

from engine_v1.datamodel import (
    Role, Message, Conversation, ActionType, 
    Logger
)
from .datamodel import (
    Config, 
    InputUser, ManualAPIHandler, PDLBot, ConversationInfos
)
from .pdl import PDL



class ConversationController:
    cfg: Config = None
    user: InputUser = None
    bot: PDLBot = None
    api: ManualAPIHandler = None
    logger: Logger = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.user = InputUser()
        self.bot = PDLBot(cfg=cfg)
        self.api = ManualAPIHandler()
        self.logger = Logger()      # TODO:
    
    def next_role(self, curr_role:Role, action_type) -> Role:
        if action_type == ActionType.START:
            return Role.USER

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
        msg_hello = Message(Role.BOT, f"你好，我是{self.cfg.workflow_name}机器人，有什么可以帮您?")
        self.logger.log(msg_hello.to_str(), with_print=True)
        conversation = Conversation()
        conversation.add_message(msg_hello)
        conversation_infos = ConversationInfos.from_components(             # useful information for bot
            previous_action_type=ActionType.START, num_user_query=0
        )
        curr_role, curr_action_type = Role.USER, ActionType.START
        action_metas = None
        while curr_action_type != ActionType.ANSWER:
            next_role = self.next_role(curr_role, curr_action_type)
            if next_role == Role.USER:
                action_type, action_metas, msg = self.user.process(conversation=conversation, pdl=pdl)
                conversation_infos.num_user_query += 1
            elif next_role == Role.BOT:
                action_type, action_metas, msg = self.bot.process(conversation=conversation, pdl=pdl, conversation_infos=conversation_infos)
            elif next_role == Role.SYSTEM:
                action_type, action_metas, msg = self.api.process(conversation=conversation, paras=action_metas)
            else:
                raise ValueError(f"Unknown role: {next_role}")
            curr_role, curr_action_type = next_role, action_type
            conversation_infos.previous_action_type = curr_action_type
            conversation.add_message(msg)
            self.logger.log(msg.to_str(), with_print=True if curr_role!=Role.USER else False)

        return conversation
    
    def start_conversation(self):
        # [1] workflow_name -> PDL
        pdl = PDL.load_from_file(f"{self.cfg.workflow_dir}/{self.cfg.workflow_name}.txt")
        
        # [2] print the header information
        t_now = datetime.datetime.now()
        infos = {
            "workflow_name": self.cfg.workflow_name,
            "model_name": self.cfg.model_name,
            "template_fn": self.cfg.template_fn,
            "workflow_dir": self.cfg.workflow_dir,
            "log_file": self.logger.log_fn,
            "time": t_now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        s_infos = "\n".join([f"{k}: {v}" for k, v in infos.items()]) + "\n"
        infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
        self.logger.log(infos_header, with_print=True)

        # [3] start! 
        conversation = self.conversation(pdl)

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)
        return infos, conversation
        