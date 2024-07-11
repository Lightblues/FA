
import os, sys, time, datetime
from typing import List, Dict, Optional, Tuple
from .common import DIR_data, LLM_stop
from .datamodel import PDL, Logger, Role, Message, Conversation
from .prompts import get_query_PDL_prompt
from .apis import BaseAPIHandler, ManualAPIHandler, LLMAPIHandler, VanillaCallingAPIHandler
from easonsi.llm.openai_client import OpenAIClient, Formater


class Agent:
    logger: Logger = None
    client: OpenAIClient = None
    api_handler: BaseAPIHandler = None
    workflow_id_map: Dict[str, str] = None
    template_fn: str = None
    
    def __init__(self, client: OpenAIClient=None, api_mode="llm", template_fn="query_PDL.jinja"):
        self.client = client
        if api_mode == "manual":
            self.api_handler = ManualAPIHandler()
        elif api_mode == "llm":
            self.api_handler = LLMAPIHandler(client)
        elif api_mode == "vanilla":
            self.api_handler = VanillaCallingAPIHandler()
        else:
            raise ValueError(f"Unknown api_mode: {api_mode}")
        self.logger = Logger()
        self.workflow_id_map = self._load_workflow_list()
        self.template_fn = template_fn

    def process_response(self, conversation:Conversation, parsed_response:dict) -> Tuple[Tuple, List[Message]]:
        action_type = parsed_response["action_type"]
        
        messages = []
        action_name, action_paras, response = parsed_response.get("action_name", "DEFTAULT_ACTION"), parsed_response.get("action_parameters", "DEFAULT_PARAS"), parsed_response.get("response", "DEFAULT_RESPONSE")
        if action_type == "API":
            res = self.api_handler.process_query(conversation, action_name, action_paras)
            messages += (
                Message(Role.BOT, f"<Call API> {action_name}({action_paras})"),
                Message(Role.SYSTEM, f"{res}"),
            )

        elif action_type in ["ANSWER", "REQUEST"]:
            messages.append(
                Message(Role.BOT, response)
            )
        else:
            print(f"[ERROR] Unknown action_type: {parsed_response['action_type']}\n{parsed_response}")
        return action_type, messages

    def _load_workflow_list(self, ):
        workflow_id_map = {}
        for file in os.listdir(DIR_data):
            if file.endswith(".txt"):
                workflow_name = file.rstrip(".txt")
                id, name = workflow_name.split("-", 1)
                workflow_id_map[id] = workflow_name
                workflow_id_map[name] = workflow_name
                workflow_id_map[workflow_name] = workflow_name
        return workflow_id_map

    def conversation(self, workflow_name="008-寄快递"):
        # proces and load PDL
        if workflow_name not in self.workflow_id_map:
            print(f"Unknown workflow_name: {workflow_name}! Please choose from {self.workflow_id_map}")
            return
        workflow_name = self.workflow_id_map[workflow_name]
        pdl = PDL()
        pdl.load_from_file(f"{DIR_data}/{workflow_name}.txt")

        # print the header information
        infos_header = f"{'='*50}\n"
        infos_header += f"workflow_name: {workflow_name}\n"
        infos_header += f"model_name: {self.client.model_name}\n"
        infos_header += f"template_fn: {self.template_fn}\n"
        infos_header += f"log_file: {self.logger.log_fn}\n"
        infos_header += f"time: {datetime.datetime.now()}\n"
        infos_header += f" START! ".center(50, "=")
        self.logger.log(infos_header, with_print=True)

        # the main loop
        conversation = Conversation()
        action_type = "START"
        while action_type != "ANSWER":
            if action_type != "API":    # If previous action is API, then call bot again
                user_input = input("[USER] ")
                msg = Message(Role.USER, user_input)
                conversation.add_message(msg)
                self.logger.log(msg.to_str(), with_print=False)
            
            # call the agent
            prompt = get_query_PDL_prompt(conversation.to_str(), pdl, template_fn=self.template_fn)
            llm_response = self.client.query_one_stream(prompt, stop=LLM_stop)
            _debug_msg = f"{'='*50}\n<<prompt>>\n{prompt}\n\n<<response>>\n{llm_response}\n"
            self.logger.debug(_debug_msg)
            # parse the generated response
            errcode, parsed_response = Formater.parse_llm_output_json(llm_response)
            a_type, msgs = self.process_response(conversation, parsed_response)
            conversation += msgs
            for msg in msgs:
                self.logger.log(msg.to_str(), with_print=True)

            action_type = a_type        # update the state 

        infos_end = f" END! ".center(50, "=")
        self.logger.log(infos_end, with_print=True)
