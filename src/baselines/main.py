""" updated @240904
- basic implementations
    - [x] BaselineController logic @240905
    - [x] logging and metrics -> append prompts to Message
    - [x] data: Workflow abstraction | align with FlowBench 
    - [x] user: add user profiling? aware of workflow?
    - [x] bot implementation
    - [x] api: mimic by LLM? 
- data
    - [ ] convert from v240820
    - [x] dataset orginization (Datamanager)
    - [ ] whole generation | simulation
    - [ ] store the generated conversation data in a database! (with a session_id)

------------------------------ abstraction ------------------------------
Conversation:
    .add_message(msg)
    .to_str()
    .get_last_message()

BaseRole:
    name; cfg; llm; conv; workflow; 
    .process() -> UserOutput, BotOutput, APIOutput
BotOutput: 
    action_type; action; action_input; thought;
    
Workflow:
    name; 
"""
import time, datetime, os, sys, tabulate
import pandas as pd
from .data import (
    Config, BotOutput, UserOutput, BotOutputType, APIOutput
)
from .roles import (
    BaseRole, BaseBot, BaseUser, BaseAPIHandler, InputUser, 
    USER_NAME2CLASS, BOT_NAME2CLASS, API_NAME2CLASS, 
)
from .data import Workflow
from engine import (
    Role, Message, Conversation, ActionType, ConversationInfos, Logger, BaseLogger
)
from utils.wrappers import Timer

class BaselineController:
    cfg: Config = None
    user: BaseUser = None
    bot: BaseBot = None
    api: BaseAPIHandler = None
    logger: Logger = None
    conv: Conversation = None       # global variable for conversation
    workflow: Workflow = None
    conversation_id: str = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.workflow = Workflow.load_by_id(
            id=cfg.workflow_id, type=cfg.workflow_type,
            load_user_profiles=cfg.user_profile
        )
        self.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.conv = Conversation(conversation_id=self.conversation_id)
        self.logger = BaseLogger()
        self.user = USER_NAME2CLASS[cfg.user_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
        self.bot = BOT_NAME2CLASS[cfg.bot_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
        self.api = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
    
    def conversation(self) -> Conversation:
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
                with Timer("user process", print=self.cfg.log_utterence_time):
                    user_output: UserOutput = self.user.process()
                # ...infos, log
                self.log_msg(self.conv.get_last_message())
                role = Role.BOT
                if user_output.is_end:
                    print(f"  <main> ended by user!")
                    break
            elif role == Role.BOT:
                num_bot_actions = 0
                while True:         # limit the bot prediction steps
                    with Timer("bot process", print=self.cfg.log_utterence_time):
                        bot_output: BotOutput = self.bot.process()
                    self.log_msg(self.conv.get_last_message())
                    if bot_output.action_type == BotOutputType.RESPONSE:
                        break
                    elif bot_output.action_type == BotOutputType.ACTION:
                        # ... call the API, append results to conversation
                        with Timer("api process", print=self.cfg.log_utterence_time):
                            api_output: APIOutput = self.api.process(bot_output)
                        self.log_msg(self.conv.get_last_message())
                    else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
                    
                    num_bot_actions += 1
                    if num_bot_actions > self.cfg.bot_action_limit: 
                        # ... the default response
                        print(f"  <main> bot retried actions reach limit!")
                        break
                role = Role.USER
            num_turns += 1
            if num_turns > self.cfg.conversation_turn_limit: 
                print("  <main> end due to conversation turn limit!")
                break
        
        return self.conv

    def log_msg(self, msg:Message):
        content = msg.to_str()      # or msg is str?
        role = msg.role
        self.logger.log(content, with_print=False)
        if not (
            isinstance(self.user, InputUser) and (role == Role.USER)
        ): 
            self.logger.log_to_stdout(content, color=role.color)
    
    def start_conversation(self):
        infos = {
            # "workflow_name": self.cfg.workflow_name,
            # "model_name": self.cfg.model_name,
            # "template_fn": self.cfg.template_fn,
            # "workflow_dir": self.cfg.workflow_dir,
            "log_file": self.logger.log_fn,
            "conversation_id": self.conversation_id,
            "config": self.cfg.to_dict(),
        }
        # s_infos = "\n".join([f"{k}: {v}" for k, v in infos.items()]) + "\n"
        # infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
        infos_header = tabulate.tabulate(pd.DataFrame([infos]).T, tablefmt='psql', maxcolwidths=100)
        self.logger.log(infos_header, with_print=True)

        conversation = self.conversation()      # main loop!
        
        # if self.cfg.

        conversation_df = pd.DataFrame(conversation.to_list())[['role', 'content']].set_index('role')
        infos_end = tabulate.tabulate(conversation_df, tablefmt='psql', maxcolwidths=100)
        self.logger.log(infos_end, with_print=True)
        return infos, conversation
    