""" 
240716: 改名为 CLIInterface, 抽象基类
"""

import os, sys, time, datetime
from typing import List, Dict, Optional, Tuple
from easonsi.llm.openai_client import OpenAIClient, Formater

from .common import DIR_data
from .datamodel import (
    PDL, Role, Message, Conversation, ActionType, BaseUser, InputUser, 
    Logger, BaseLogger
)
from .apis import BaseAPIHandler, ManualAPIHandler, LLMAPIHandler, VanillaCallingAPIHandler
from .bots import PDLBot


class CLIInterface:
    logger: Logger = None
    user_agent: BaseUser = None
    workflow_id_map: Dict[str, str] = None
    client: OpenAIClient = None
    bot = None
    
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
        self.workflow_id_map = self._load_workflow_list(self.workflow_dir)
        self.user_agent = InputUser()
        self.client = client
        self.bot = PDLBot(client, api_handler, logger=self.logger, template_fn=template_fn)

    def _load_workflow_list(self, config_dir:str):
        workflow_id_map = {}
        for file in os.listdir(config_dir):
            if file.endswith(".txt"):
                workflow_name = file.rstrip(".txt")
                id, name = workflow_name.split("-", 1)
                workflow_id_map[id] = workflow_name
                workflow_id_map[name] = workflow_name
                workflow_id_map[workflow_name] = workflow_name
        return workflow_id_map

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
        action_type = ActionType.START
        while action_type != ActionType.ANSWER:
            if action_type != ActionType.API:    # If previous action is API, then call bot again
                msg = self.user_agent.generate(conversation)
                self.logger.log(msg.to_str(), with_print=False)
            
            _a_type, msgs = self.bot.process(conversation)
            for msg in msgs:
                self.logger.log(msg.to_str(), with_print=True)
            action_type = _a_type        # update the state 

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)
