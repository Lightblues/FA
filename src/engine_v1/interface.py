""" 
@240716: 改名为 CLIInterface, 抽象基类
"""

import os, sys, time, datetime
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from .common import DIR_data, DataManager
from .datamodel import (
    PDL, Role, Message, Conversation, ActionType, BaseUser, InputUser, 
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



    def conversation(self, workflow_name="008-寄快递"):
        # process and load PDL
        if workflow_name not in self.workflow_id_map:
            print(f"Unknown workflow_name: {workflow_name}! Please choose from {self.workflow_id_map}")
            return
        workflow_name = self.workflow_id_map[workflow_name]
        pdl_fn = f"{self.workflow_dir}/{workflow_name}.txt"
        self.bot._load_pdl(pdl_fn)

        # print the header information
        infos_header = f"{'='*50}\n"
        infos_header += f"workflow_name: {workflow_name}\n"
        infos_header += f"model_name: {self.client.model_name}\n"
        infos_header += f"template_fn: {self.bot.template_fn}\n"
        infos_header += f"workflow_dir: {self.workflow_dir}\n"
        infos_header += f"log_file: {self.logger.log_fn}\n"
        infos_header += f"time: {datetime.datetime.now()}\n"
        infos_header += f" START! ".center(50, "=")
        self.logger.log(infos_header, with_print=True)

        # the main loop
        conversation = Conversation()
        current_action_type = ActionType.START
        while current_action_type != ActionType.ANSWER:
            if current_action_type != ActionType.API:    # If previous action is API, then call bot again
                msg = self.user.generate(conversation)
                self.logger.log(msg.to_str(), with_print=False)
            
            action_type, msgs = self.bot.process(conversation)
            for msg in msgs:
                self.logger.log(msg.to_str(), with_print=True)
            current_action_type = action_type        # update the state 

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)
