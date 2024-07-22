""" 
@240716: ConversationSimulatorLLMUser
"""
from typing import List, Dict, Optional
from easonsi.llm.openai_client import OpenAIClient, Formater

from engine_v1.datamodel import Conversation, BaseUser, Message, Role, Logger
from utils.jinja_templates import jinja_render


class ConversationSimulatorLLMUser(BaseUser):
    ref_conversation: Conversation
    client: OpenAIClient
    
    
    def __init__(self, ref_conversation:Conversation, client:OpenAIClient, logger:Logger) -> None:
        self.ref_conversation = ref_conversation
        self.client = client
        self.logger = logger

    def generate(self, conversation:Conversation) -> Message:
        """ 根据当前的会话进度, 生成下一轮query """
        prompt = jinja_render(
            "user_simulator.jinja",
            ref_conversation=self.ref_conversation.to_str(),
            new_conversation=conversation.to_str(),
        )
        llm_response = self.client.query_one_stream(prompt)
        _debug_msg = f"{'[USER]'.center(50, '=')}\n<<prompt>>\n{prompt}\n\n<<response>>\n{llm_response}\n"
        self.logger.debug(_debug_msg)
        try:
            parsed_response = Formater.parse_llm_output_json(llm_response)
            content = parsed_response["content"]
            msg = Message(role=Role.USER, content=content)
            conversation.add_message(msg)       # NOTE to update the conversation
            return msg
        except Exception as e:
            raise ValueError(f"Error parsing LLM response: {llm_response}")
