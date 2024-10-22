import re
import os
import time
from tqdm import tqdm
import json
import pandas as pd
import datetime
import argparse
from typing import Optional, List
from tabulate import tabulate

from flowagent.utils import init_client, LLM_CFG, OpenAIClient, Formater
from utils.jinja_templates import jinja_render

# class for transforming workflow format
class FormatTransformer:
    llm: OpenAIClient = None
    template_file: str = None
    return_codeblock_format: str = None   # python, PDL, mermaid, ...
    
    def __init__(self, model_name, template_file, return_format) -> None:
        self.llm = init_client(llm_cfg=LLM_CFG[model_name])
        self.template_file = template_file
        self.return_codeblock_format = return_format
    
    def transform(self, NL_desc: dict, apis: list) -> str:
        NL_desc['available_apis'] = apis
        
        prompt = jinja_render(
            self.template_file,
            NL=json.dumps(NL_desc, indent=2)
        )
        # print('=' * 20 + 'prompt ' + '=' * 20)
        # print(prompt)
        llm_resp = self.llm.query_one(prompt)
        # print('=' * 20 + ' resp ' + '=' * 20)
        # print(llm_resp)
        
        workflow = Formater.parse_codeblock(llm_resp, self.return_codeblock_format)
        return workflow


# class for transforming API format
class APITransformer:
    llm: OpenAIClient = None
    template_file: str = None
    
    def __init__(self, model_name, template_file, return_format) -> None:
        self.llm = init_client(llm_cfg=LLM_CFG[model_name])
        self.template_file = template_file
    
    def transform(self, api: dict) -> str:
        prompt = jinja_render(
            self.template_file,
            API=json.dumps(api, indent=2)
        )
        # print('=' * 20 + 'prompt ' + '=' * 20)
        # print(prompt)
        llm_resp = self.llm.query_one(prompt)
        # print('=' * 20 + ' resp ' + '=' * 20)
        # print(llm_resp)
        
        transformed_api = Formater.parse_llm_output_json(llm_resp)
        return transformed_api
