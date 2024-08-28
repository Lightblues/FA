import requests, json, traceback
from typing import List, Dict, Optional, Tuple

from .datamodel import BaseRole, Config, Role, Message, Conversation, PDL, ActionType
from .common import prompt_user_input, _DIRECTORY_MANAGER, init_client, LLM_CFG, DEBUG
from .typings import APIActionMetas, APICalling_Info
from easonsi.llm.openai_client import OpenAIClient, Formater
from utils.jinja_templates import jinja_render


class EntityLinker:
    """ abstract of entity linking """
    cfg: Config = None
    llm: OpenAIClient
    
    def __init__(self, cfg:Config) -> None:
        self.cfg = cfg
        self.llm = init_client(llm_cfg=LLM_CFG[cfg.api_model_name])
        if DEBUG: print(f">> [api] init EL model {cfg.api_model_name} with {json.dumps(LLM_CFG[cfg.api_model_name], ensure_ascii=False)}")

    def entity_linking(self, query:str, eneity_list: List[str]) -> Dict:
        """ Given a list of candidate entities, use llm to determine which one is most similor to the input
        return : 
        """
        meta = {}
        
        # if DEBUG: print(f">> runing EL for {query} with {json.dumps(eneity_list, ensure_ascii=False)}")
        res = {
            "is_matched": True, 
            "matched_entity": None
        }
        prompt = jinja_render("entity_linking.jinja", query=query, eneity_list=eneity_list)
        # if DEBUG: print(f"  model: {self.llm}\n  prompt: {json.dumps(prompt, ensure_ascii=False)}")
        llm_response = self.llm.query_one(prompt)
        # if DEBUG: print(f"  llm_response: {json.dumps(llm_response, ensure_ascii=False)}")
        meta.update(prompt=prompt, llm_response=llm_response)
        
        # todo: error handling
        parsed_response = Formater.parse_llm_output_json(llm_response)
        if parsed_response["is_matched"]: res["matched_entity"] = parsed_response["matched_entity"]
        else: res["is_matched"] = False
        return res, meta

