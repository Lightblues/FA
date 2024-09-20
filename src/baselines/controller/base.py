""" updated @240919
"""

from abc import abstractmethod
from typing import List
import tabulate, datetime
import pandas as pd
from ..data import (
    Config, DBManager, DataManager, Workflow,
    Role, Message, Conversation, Logger, BaseLogger
)
from ..roles import InputUser, BaseBot, BaseUser, BaseAPIHandler

class BaseController:
    """ main loop of a simulated conversation
    USAGE:
        controller = XXXController(cfg)
        controller.start_conversation()
    """
    cfg: Config = None
    user: BaseUser = None
    bot: BaseBot = None
    api: BaseAPIHandler = None
    logger: Logger = None
    conv: Conversation = None       # global variable for conversation
    data_namager: DataManager = None
    workflow: Workflow = None
    conversation_id: str = None
    
    workflow_types: List[str] = None    # to build WORKFLOW_TYPE2CONTROLLER
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.data_namager = DataManager(cfg)
        self.logger = BaseLogger()
        self.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.conv = Conversation(conversation_id=self.conversation_id)
    
    @abstractmethod
    def conversation(self, verbose:bool=True) -> Conversation:
        raise NotImplementedError()
    
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
            query = {  # identify a single exp
                "exp_version": self.cfg.exp_version,
                **{ k:v for k,v in self.cfg.to_dict().items() if k.startswith("workflow") },
                "user_profile_id": self.cfg.user_profile_id
            }
            query_res = db.query_run_experiments(query)
            if len(query_res) > 0:
                self.logger.log(f"NOTE: the experiment has already been run!", with_print=verbose)
                return infos, None  # the returned results haven't been used

        conversation = self.conversation(verbose=verbose)
        
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
    
    def log_msg(self, msg:Message, verbose=True):
        """ log message to logger and stdout """
        _content = msg.to_str()      # or msg is str?
        self.logger.log(_content, with_print=False)
        if verbose and not (    # for InputUser, no need to print
            isinstance(self.user, InputUser) and (msg.role == Role.USER)
        ): 
            self.logger.log_to_stdout(_content, color=msg.role.color)
