from .datamodel import PDL, Logger, Role, Message, Conversation
from utils.jinja_templates import jinja_render


def get_query_PDL_prompt(s_conversation:str, pdl:PDL):
    prompt = jinja_render(
        "query_PDL.jinja",
        PDL=pdl.to_str(),
        conversation=s_conversation
    )
    return prompt

def get_llm_API_prompt(s_conversation:str, api_name: str, api_params: str):
    prompt = jinja_render(
        "api_llm_v1.jinja",
        conversation=s_conversation,
        api_name=api_name,
        api_params=api_params
    )
    return prompt