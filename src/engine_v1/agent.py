
import os, sys, time, datetime
from typing import List, Dict, Optional, Tuple
from .common import DIR_data
from .datamodel import PDL, Logger, Role, Message, Conversation
from .apis import ManualAPIhandler
from utils.jinja_templates import jinja_render
from easonsi.llm.openai_client import OpenAIClient, Formater

client = None
logger = Logger()

def init_client(llm_cfg:Dict):
    global client
    base_url = os.getenv("OPENAI_PROXY_BASE_URL") if llm_cfg.get("base_url") is None else llm_cfg["base_url"]
    api_key = os.getenv("OPENAI_PROXY_API_KEY") if llm_cfg.get("api_key") is None else llm_cfg["api_key"]
    model_name = llm_cfg.get("model_name", "gpt-4o")
    client = OpenAIClient(
        model_name=model_name, base_url=base_url, api_key=api_key
    )
    return client

api_handler = ManualAPIhandler()


def get_query_PDL_prompt(s_conversation:str, pdl:PDL):
    prompt = jinja_render(
        "query_PDL.jinja",
        PDL=pdl.to_str(),
        conversation=s_conversation
    )
    return prompt

def process_response(conversation:Conversation, parsed_response) -> Tuple[Tuple, List[Message]]:
    action_type = parsed_response["action_type"]
    
    messages = []
    action_name, action_paras, response = parsed_response["action_name"], parsed_response["action_parameters"], parsed_response["response"]
    if action_type == "API":
        res = api_handler.process_query(conversation, action_name, action_paras)
        messages += (
            Message(Role.BOT, f"<Call API> {action_name}({action_paras}"),
            Message(Role.SYSTEM, f"{res}"),
        )

    elif action_type in ["ANSWER", "REQUEST"]:
        messages.append(
            Message(Role.BOT, response)
        )
    else:
        print(f"[ERROR] Unknown action_type: {parsed_response['action_type']}\n{parsed_response}")
    return action_type, messages



def conversation(workflow_name="008-寄快递"):
    pdl = PDL()
    pdl.load_from_file(f"{DIR_data}/{workflow_name}.txt")

    infos_start = f"{'='*50}\n"
    infos_start += f"workflow_name: {workflow_name}\n"
    infos_start += f"time: {datetime.datetime.now()}\n"
    infos_start += f" START! ".center(50, "=")
    logger.log(infos_start, with_print=True)

    conversation = Conversation()
    action_type = "START"
    while action_type != "ANSWER":
        if action_type != "API":    # If previous action is API, then call bot again
            user_input = input("[USER] ")
            msg = Message(Role.USER, user_input)
            conversation.add_message(msg)
            logger.log(msg.to_str(), with_print=False)
        
        # call the agent
        prompt = get_query_PDL_prompt(conversation.to_str(), pdl)
        # llm_response = client.query_one(prompt)
        llm_response = client.query_one_stream(prompt)
        errcode, parsed_response = Formater.parse_llm_output_json(llm_response)
        a_type, msgs = process_response(conversation, parsed_response)
        conversation += msgs
        for msg in msgs:
            logger.log(msg.to_str(), with_print=True)

        action_type = a_type        # update the state 

    infos_end = f" END! ".center(50, "=")
    logger.log(infos_end, with_print=True)
