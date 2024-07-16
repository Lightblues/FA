""" 
@240716 Simulator

"""
import datetime
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater

from .api import ConversationSimulatorAPIHandler
from .useragent import ConversationSimulatorLLMUser
from engine_v1.interface import CLIInterface
from engine_v1.apis import BaseAPIHandler
from engine_v1.bots import BaseBot, PDLBot
from engine_v1.common import DIR_data, DIR_simulation, DataManager
from engine_v1.datamodel import (
    Conversation, Logger, BaseLogger, ActionType
)

class Simulator(CLIInterface):
    client: OpenAIClient = None
    api_handler: BaseAPIHandler = None
    user: ConversationSimulatorLLMUser = None
    bot: PDLBot = None
    logger: Logger = None
    workflow_dir: str = None
    workflow_id_map: Dict[str, str] = None
    
    def __init__(self, client: OpenAIClient=None, workflow_dir:str=DIR_data) -> None:
        self.client = client
        self.workflow_dir = workflow_dir
        self.workflow_id_map = DataManager.build_workflow_id_map(self.workflow_dir)
        self.logger = Logger(log_dir=DIR_simulation)        # specify the log dir!

    def simulate(self, workflow_name:str, ref_conversation:Conversation):
        """ Given a conversation, run the simulation """
        self.api_handler = ConversationSimulatorAPIHandler(ref_conversation, self.client, self.logger)
        self.user = ConversationSimulatorLLMUser(ref_conversation, self.client, self.logger)
        self.bot = PDLBot(self.client, self.api_handler, self.logger, template_fn="query_PDL.jinja")

        workflow_name = self.workflow_id_map[workflow_name]
        pdl_fn = f"{self.workflow_dir}/{workflow_name}.txt"
        self.bot._load_pdl(pdl_fn)


        infos_header = f"{'='*50}\n"
        infos_header += f"workflow_name: {workflow_name}\n"
        infos_header += f"model_name: {self.client.model_name}\n"
        infos_header += f"template_fn: {self.bot.template_fn}\n"
        infos_header += f"workflow_dir: {self.workflow_dir}\n"
        infos_header += f"log_file: {self.logger.log_fn}\n"
        infos_header += f"time: {datetime.datetime.now()}\n"
        infos_header += f" START! ".center(50, "=")
        self.logger.log(infos_header, with_print=True)
        
        conversation = Conversation()
        current_action_type = ActionType.START
        while current_action_type != ActionType.ANSWER:
            if current_action_type != ActionType.API:
                msg = self.user.generate(conversation)
                self.logger.log(msg.to_str(), with_print=True)  # print the 'user' input
            action_type, msgs = self.bot.process(conversation)
            for msg in msgs:
                self.logger.log(msg.to_str(), with_print=True)
            current_action_type = action_type        # update the state 

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)