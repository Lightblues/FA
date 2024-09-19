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
    - [x] whole generation | simulation
    - [x] store the generated conversation data in a database! (with a session_id)
- evaluation
    - [x] start simulations. 
- robustness & accuracy
    - [x] add retry for API or bot? -> how to evaluate?
    - [x] user simulation: make simulated user to be more realistic (shorter utterance, ...)
    - [ ] API: refine the prompt of API simulator

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
    Config, BotOutput, UserOutput, BotOutputType, APIOutput,
    Workflow, DBManager, DataManager
)
from .roles import (
    BaseRole, BaseBot, BaseUser, BaseAPIHandler, InputUser, 
    USER_NAME2CLASS, BOT_NAME2CLASS, API_NAME2CLASS, 
)
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
    data_namager: DataManager = None
    workflow: Workflow = None
    conversation_id: str = None
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.data_namager = DataManager(cfg)
        self.workflow = Workflow.load_by_id(
            data_manager=self.data_namager,
            id=cfg.workflow_id, type=cfg.workflow_type,
            load_user_profiles=cfg.user_profile
        )
        self.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.conv = Conversation(conversation_id=self.conversation_id)
        self.logger = BaseLogger()
        self.user = USER_NAME2CLASS[cfg.user_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
        self.bot = BOT_NAME2CLASS[cfg.bot_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
        self.api = API_NAME2CLASS[cfg.api_mode](cfg=cfg, conv=self.conv, workflow=self.workflow)
    
    def conversation(self, verbose:bool=True) -> Conversation:
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
                self.log_msg(self.conv.get_last_message(), verbose=verbose)
                role = Role.BOT
                if user_output.is_end:
                    self.logger.log(f"  <main> ended by user!", with_print=verbose)
                    break
            elif role == Role.BOT:
                num_bot_actions = 0
                while True:         # limit the bot prediction steps
                    with Timer("bot process", print=self.cfg.log_utterence_time):
                        bot_output: BotOutput = self.bot.process()
                    self.log_msg(self.conv.get_last_message(), verbose=verbose)
                    if bot_output.action_type == BotOutputType.RESPONSE:
                        break
                    elif bot_output.action_type == BotOutputType.ACTION:
                        # ... call the API, append results to conversation
                        with Timer("api process", print=self.cfg.log_utterence_time):
                            api_output: APIOutput = self.api.process(bot_output)
                        self.log_msg(self.conv.get_last_message(), verbose=verbose)
                    else: raise TypeError(f"Unexpected BotOutputType: {bot_output.action_type}")
                    
                    num_bot_actions += 1
                    if num_bot_actions > self.cfg.bot_action_limit: 
                        # ... the default response
                        self.logger.log(f"  <main> bot retried actions reach limit!", with_print=verbose)
                        break
                role = Role.USER
            num_turns += 1
            if num_turns > self.cfg.conversation_turn_limit: 
                self.logger.log("  <main> end due to conversation turn limit!", with_print=verbose)
                break
        
        return self.conv

    def log_msg(self, msg:Message, verbose=True):
        content = msg.to_str()      # or msg is str?
        role = msg.role
        self.logger.log(content, with_print=False)
        if verbose and not (
            isinstance(self.user, InputUser) and (role == Role.USER)
        ): 
            self.logger.log_to_stdout(content, color=role.color)
    
    def start_conversation(self, verbose=True):
        infos = {
            "conversation_id": self.conversation_id,
            "exp_version": self.cfg.exp_version,
            "log_file": self.logger.log_fn,
            "config": self.cfg.to_dict(),
        }
        infos_header = tabulate.tabulate(pd.DataFrame([infos]).T, tablefmt='psql', maxcolwidths=100)
        self.logger.log(infos_header, with_print=verbose)

        # check if run!
        if self.cfg.log_to_db:
            db = DBManager(self.cfg.db_uri, self.cfg.db_name, self.cfg.db_message_collection_name)
            query = {
                "exp_version": self.cfg.exp_version,
                **{ k:v for k,v in self.cfg.to_dict().items() if k.startswith("workflow") },
            }
            query_res = db.query_run_experiments(query)
            if len(query_res) > 0:
                self.logger.log(f"NOTE: the experiment has already been run!", with_print=verbose)
                return infos, None  # the returned results haven't been used

        conversation = self.conversation(verbose=verbose)      # main loop!
        
        if self.cfg.log_to_db:
            db = DBManager(self.cfg.db_uri, self.cfg.db_name, self.cfg.db_message_collection_name)
            # 1. insert conversation
            res = db.insert_conversation(conversation)
            self.logger.log(f"  <db> Inserted conversation with {len(res.inserted_ids)} messages", with_print=verbose)
            # 2. insert configuration
            infos_dict = {
                "conversation_id": self.conversation_id, "exp_version": self.cfg.exp_version, "log_file": self.logger.log_fn, 
                **self.cfg.to_dict()
            }
            res = db.insert_config(infos_dict)
            self.logger.log(f"  <db> Inserted config", with_print=verbose)

        conversation_df = pd.DataFrame(conversation.to_list())[['role', 'content']].set_index('role')
        infos_end = tabulate.tabulate(conversation_df, tablefmt='psql', maxcolwidths=100)
        self.logger.log(infos_end, with_print=verbose)
        return infos, conversation
    