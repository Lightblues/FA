from typing import Iterator

import requests

from ..typings import BotOutput, MultiToolMainResponse
from .client_base import BaseClient


class ToolAgentMixin(BaseClient):
    """
    Usage::

        client = ToolAgentMixin(url="http://localhost:8100")
        bot_output = BotOutput(action="hunyuan_search", action_input={"query": "感冒"})
        stream = client.multi_tool_main_stream("xxx", bot_output)  # ... process the stream
        res = client.multi_tool_main_output("xxx")
    """

    def multi_tool_main(self, conversation_id: str, bot_output: BotOutput) -> MultiToolMainResponse:
        url = f"{self.backend_url}/multi_tool_main/{conversation_id}"
        response = requests.post(url, json=bot_output.model_dump())
        if response.status_code == 200:
            res = MultiToolMainResponse(**response.json())
            self.conv.add_message(res.msg)
            return res
        else:
            raise NotImplementedError

    def multi_tool_main_stream(self, conversation_id: str, bot_output: BotOutput) -> Iterator[str]:
        url = f"{self.backend_url}/multi_tool_main_stream/{conversation_id}"
        return self.process_stream_url(url, bot_output.model_dump())

    def multi_tool_main_output(self, conversation_id: str) -> MultiToolMainResponse:
        url = f"{self.backend_url}/multi_tool_main_output/{conversation_id}"
        response = requests.get(url)
        if response.status_code == 200:
            res = MultiToolMainResponse(**response.json())
            self.conv.add_message(res.msg)
            return res
        else:
            raise NotImplementedError
