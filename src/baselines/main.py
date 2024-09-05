""" updated @240904
- basic implementations
    - [ ] BaselineController logic
    - [ ] data: Workflow abstraction
    - [ ] user: add user profiling? aware of workflow?
    - [ ] bot implementation
    - [ ] api: mimic by LLM? 
- data
    - [ ] convert from v240820
    - [ ] dataset orginization (Datamanager)

------------------------------ abstraction ------------------------------
Conversation:
    .add_message(msg)
    .to_str()
    .last_message()
"""
import time, datetime, os, sys, tabulate
import pandas as pd
from .common import (
    Config, Workflow,
    BotOutput, UserOutput, BotOutputType, APIOutput
)
from .roles import BaseRole, BaseBot, BaseUser, BaseAPIHandler, USER_NAME2CLASS, BOT_NAME2CLASS, API_NAME2CLASS
from engine import (
    Role, Message, Conversation, ActionType, ConversationInfos, Logger, BaseLogger
)

class BaselineController:
    cfg: Config = None
    user: BaseUser = None
    bot: BaseBot = None
    api: BaseAPIHandler = None
    logger: Logger = None
    conv: Conversation = None       # global variable for conversation
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.conv = Conversation()
        self.logger = BaseLogger()
        self.user = USER_NAME2CLASS[cfg.user_mode](cfg=cfg, conv=self.conv)
        self.bot = BOT_NAME2CLASS[cfg.bot_mode](cfg=cfg, conv=self.conv)
        self.api = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=self.conv)
    
    def conversation(self, workflow: Workflow=None):
        """ 
        1. initiation: initialize the variables, logger, etc.
        2. main loop
            stop: by user (or bot?) -- only user!
            controller: 
                > bot can take several actions in one turn? 
        """
        # ...init, log meta infos
        role: Role = Role.USER      # current role!
        
        num_turns:int = 0           # cnt of user & bot conversation
        # cnt_utterance:int = 0       # cnt of u/b/s utterance (conversation length)
        while True:
            if role == Role.USER:
                user_output: UserOutput = self.user.process()
                # ...infos, log
                self.log_msg(self.conv.get_last_message())
                role = Role.BOT
            elif role == Role.BOT:
                num_bot_actions = 0
                while True:         # limit the bot prediction steps
                    bot_output: BotOutput = self.bot.process()
                    self.log_msg(self.conv.get_last_message())
                    if bot_output.action_type == BotOutputType.RESPONSE:
                        break
                    elif bot_output.action_type == BotOutputType.ACTION:
                        # ... call the API, append results to conversation
                        api_output: APIOutput = self.api.process(bot_output.action, bot_output.action_input)
                        self.log_msg(self.conv.get_last_message())
                    else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
                    
                    num_bot_actions += 1
                    if num_bot_actions > self.cfg.bot_action_limit: 
                        # ... the default response
                        break
                role = Role.USER
            num_turns += 1
            if num_turns > self.cfg.conversation_turn_limit: break
        
        return self.conversation

    def log_msg(self, msg:Message):
        content = msg.to_str()      # or msg is str?
        role = msg.role
        self.logger.log(content, with_print=False)
        if not (
            (self.cfg.user_mode == "manual") and (role == Role.USER)
        ): 
            self.logger.log_to_stdout(content, color=role.color)
            
    def start_conversation(self):
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
        # s_infos = "\n".join([f"{k}: {v}" for k, v in infos.items()]) + "\n"
        # infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
        infos_header = tabulate.tabulate(pd.DataFrame([infos]).T, tablefmt='psql')
        self.logger.log(infos_header, with_print=True)

        conversation = self.conversation()

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)
        return infos, conversation
        