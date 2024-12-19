"""updated @240919"""

import datetime
from abc import abstractmethod

import pandas as pd
from loguru import logger

from common import Config, LogUtils

from ..data import (
    Conversation,
    DataHandler,
    DataManager,
    DBManager,
    Message,
    Role,
)
from ..roles import BaseBot, BaseTool, BaseUser, InputUser


class BaseConversationManager:
    """main loop of a simulated conversation
    USAGE:
        cm = XXXConversationManager(cfg)
        cm.start_conversation()
    """

    cfg: Config = None
    user: BaseUser = None
    bot: BaseBot = None
    api: BaseTool = None
    conv: Conversation = None  # global variable for conversation
    data_manager: DataManager = None  # remove it?
    workflow: DataHandler = None
    conversation_id: str = None

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.data_manager = DataManager(cfg)
        self.conversation_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.conv = Conversation(conversation_id=self.conversation_id)

        if self.cfg.log_to_db:
            self.db = DBManager(self.cfg.db_uri, self.cfg.db_name, self.cfg.db_message_collection_name)

    @abstractmethod
    def conversation(self, verbose: bool = True) -> Conversation:
        raise NotImplementedError()

    @abstractmethod
    def conversation_teacher_forcing(self, verbose: bool = True) -> Conversation:
        raise NotImplementedError()

    def start_conversation(self, verbose=True):
        infos = {
            "conversation_id": self.conversation_id,
            "exp_version": self.cfg.exp_version,
            "config": self.cfg.model_dump(),
        }
        logger.log(LogUtils.format_infos_with_tabulate(infos))

        # 1. check if has been run!
        if self._check_if_already_run():
            logger.log(f"NOTE: the experiment {self.cfg.exp_version} has already been run!")
            return infos, None  # the returned results haven't been used
        # 2. run the conversation
        conversation = self.conversation(verbose=verbose)
        # 3. record the conversation
        self._record_to_db(conversation, verbose=verbose)

        conversation_df = pd.DataFrame(conversation.to_list())[["role", "content"]].set_index("role")
        logger.log(LogUtils.format_infos_with_tabulate(conversation_df))
        return infos, conversation

    def start_conversation_teacher_forcing(self, verbose=True):
        infos = {
            "conversation_id": self.conversation_id,
            "exp_version": self.cfg.exp_version,
            "config": self.cfg.model_dump(),
        }
        logger.log(LogUtils.format_infos_with_tabulate(infos))

        # 1. check if has been run!
        if self._check_if_already_run():
            logger.log(f"NOTE: the experiment {self.cfg.exp_version} has already been run!")
            return infos, None  # the returned results haven't been used
        # 2. run the conversation
        conversation = self.conversation_teacher_forcing(verbose=verbose)
        # 3. record the conversation
        self._record_to_db(conversation, verbose=verbose)

        conversation_df = pd.DataFrame(conversation.to_list())[["role", "content"]].set_index("role")
        logger.log(LogUtils.format_infos_with_tabulate(conversation_df))
        return infos, conversation

    def _check_if_already_run(self) -> bool:
        if not self.cfg.exp_check_if_run:
            return False  # DONOT check this experiment if it has been run
        query = {  # identify a single exp
            "exp_version": self.cfg.exp_version,
            "exp_mode": self.cfg.exp_mode,
            **{k: v for k, v in self.cfg.model_dump().items() if k.startswith("workflow")},
            "user_profile_id": self.cfg.user_profile_id,
        }
        if self.cfg.simulate_force_rerun:
            res = self.db.delete_run_experiments(query)
            return False
        else:
            query_res = self.db.query_run_experiments(query)
            return len(query_res) > 0

    def _record_to_db(self, conversation: Conversation, verbose=True):
        if not self.cfg.log_to_db:
            return

        # 1. insert conversation
        res = self.db.insert_conversation(conversation)
        logger.log(f"  <db> Inserted conversation with {len(res.inserted_ids)} messages")

        # 2. insert configuration
        infos_dict = {
            "conversation_id": self.conversation_id,
            "exp_version": self.cfg.exp_version,
            **self.cfg.model_dump(),
        }
        res = self.db.insert_config(infos_dict)
        logger.log(f"  <db> Inserted config")

    def log_msg(self, msg: Message, verbose=True):
        """log message to logger and stdout"""
        _content = msg.to_str()  # or msg is str?
        logger.log(_content)
        if verbose and not (  # for InputUser, no need to print
            isinstance(self.user, InputUser) and (msg.role == Role.USER)
        ):
            LogUtils.log_to_stdout(_content, color=msg.role.color)
