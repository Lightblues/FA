""" 
@240716: 改名为 CLIInterface, 抽象基类
"""

import os, sys, time, datetime
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from .common import DIR_data, DataManager
from .datamodel import (
    PDL, Role, Message, Conversation, ActionType, ConversationInfos, BaseUser, InputUser, 
    Logger, BaseLogger
)
from .apis import BaseAPIHandler, ManualAPIHandler, LLMAPIHandler, VanillaCallingAPIHandler
from .bots import PDLBot


class CLIInterface:
    client: OpenAIClient = None
    user: BaseUser = None
    bot = None
    logger: Logger = None
    workflow_dir: str = None
    workflow_id_map: Dict[str, str] = None
    
    def __init__(self, client: OpenAIClient=None, api_mode="llm", template_fn="query_PDL.jinja", workflow_dir:str=DIR_data):
        if api_mode == "manual":
            api_handler = ManualAPIHandler()
        elif api_mode == "llm":
            api_handler = LLMAPIHandler(client)
        elif api_mode == "vanilla":
            api_handler = VanillaCallingAPIHandler()
        else:
            raise ValueError(f"Unknown api_mode: {api_mode}")
        self.logger = Logger()
        self.workflow_dir = workflow_dir
        self.workflow_id_map = DataManager.build_workflow_id_map(self.workflow_dir)
        self.user = InputUser()
        self.client = client
        self.bot = PDLBot(client, api_handler, logger=self.logger, template_fn=template_fn)



    def conversation(self, workflow_name="000"):
        # process and load PDL
        if workflow_name not in self.workflow_id_map:
            print(f"Unknown workflow_name: {workflow_name}! Please choose from {self.workflow_id_map}")
            return
        workflow_name = self.workflow_id_map[workflow_name]
        pdl_fn = f"{self.workflow_dir}/{workflow_name}.txt"
        self.bot._load_pdl(pdl_fn)

        # print the header information
        t_now = datetime.datetime.now()
        infos = {
            "workflow_name": workflow_name,
            "model_name": self.client.model_name,
            "template_fn": self.bot.template_fn,
            "workflow_dir": self.workflow_dir,
            "log_file": self.logger.log_fn,
            "time": t_now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        s_infos = "\n".join([f"{k}: {v}" for k, v in infos.items()]) + "\n"
        infos_header = f"{'='*50}\n" + s_infos + " START! ".center(50, "=")
        self.logger.log(infos_header, with_print=True)

        # the main loop
        conversation = Conversation()
        conversation_infos = ConversationInfos.from_components(
            previous_action_type=ActionType.START, num_user_query=0
        )
        while conversation_infos.previous_action_type != ActionType.ANSWER:
            if conversation_infos.previous_action_type != ActionType.API:    # If previous action is API, then call bot again
                msg = self.user.generate(conversation)              # USRE input!
                self.logger.log(msg.to_str(), with_print=False)
                conversation_infos.num_user_query += 1
            
            action_type = self.bot.process(conversation, conversation_infos)
            _num_actions = 2 if action_type==ActionType.API else 1
            for msg in conversation.msgs[:-_num_actions]:
                self.logger.log(msg.to_str(), with_print=True)
            conversation_infos.previous_action_type = action_type        # update the state 

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)

        return infos, conversation

