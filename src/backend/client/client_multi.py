from typing import Dict, Iterator

import requests

from flowagent.data import BotOutput, Config, Conversation, Role

from ..typings import (
    MultiBotMainPredictResponse,
    MultiBotWorkflowPredictResponse,
    MultiPostControlResponse,
    MultiRegisterRequest,
    MultiRegisterResponse,
    MultiToolWorkflowResponse,
)
from .client_base import BaseClient


class MultiAgentMixin(BaseClient):
    """Wrapper of `backend/routers/router_multi_agent.py`

    Usage: similar to :class:`SingleAgentMixin`
        see `test/backend/test_ui_backend_multi.py`
    """

    curr_status: str = "main"

    def multi_register(self, conversation_id: str, config: Config, user_identity: Dict = None) -> Conversation:
        """Register a new conversation

        Args:
            conversation_id (str): the id of the conversation
            config (Config): the config of the conversation

        Notes:
            - reset the curr_status to "main"
        """
        self.curr_status = "main"

        url = f"{self.url}/multi_register/{conversation_id}"
        response = requests.post(
            url,
            json=MultiRegisterRequest(user_identity=user_identity, config=config).model_dump(),
        )
        if response.status_code == 200:
            result = MultiRegisterResponse(**response.json())
            self.conv = result.conversation
            return self.conv
        else:
            print(f"Error: {response.text}")
            raise NotImplementedError

    def multi_disconnect(self, conversation_id: str):
        url = f"{self.url}/multi_disconnect/{conversation_id}"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise NotImplementedError

    def multi_user_input(self, conversation_id: str, query: str):
        """Add a user message to the conversation

        Args:
            conversation_id (str): the id of the conversation
            query (str): the message of the user
        """
        self.conv.add_message(query, role=Role.USER)
        url = f"{self.url}/multi_add_message/{conversation_id}"
        response = requests.post(url, json=self.conv.get_last_message().model_dump())
        if response.status_code == 200:
            return response.json()
        else:
            raise NotImplementedError

    # ---
    def multi_bot_main_predict(self, conversation_id: str) -> Iterator[str]:
        url = f"{self.url}/multi_bot_main_predict/{conversation_id}"
        return self.process_stream_url(url)

    def multi_bot_main_predict_output(self, conversation_id: str) -> MultiBotMainPredictResponse:
        url = f"{self.url}/multi_bot_main_predict_output/{conversation_id}"
        response = requests.get(url)
        if response.status_code == 200:
            res = MultiBotMainPredictResponse(**response.json())
            self.conv.add_message(res.msg)
            # NOTE to change the curr_status if switched to a workflow!
            if res.bot_output.workflow:
                self.curr_status = res.bot_output.workflow
            return res
        else:
            raise NotImplementedError

    # ---
    def multi_bot_workflow_predict(self, conversation_id: str) -> Iterator[str]:
        url = f"{self.url}/multi_bot_workflow_predict/{conversation_id}"
        return self.process_stream_url(url)

    def multi_bot_workflow_predict_output(self, conversation_id: str) -> MultiBotWorkflowPredictResponse:
        url = f"{self.url}/multi_bot_workflow_predict_output/{conversation_id}"
        response = requests.get(url)
        if response.status_code == 200:
            res = MultiBotWorkflowPredictResponse(**response.json())
            self.conv.add_message(res.msg)
            if res.bot_output.workflow:
                self.curr_status = res.bot_output.workflow
            return res
        else:
            print(f"Error: {response.text}")
            raise NotImplementedError

    def multi_post_control(self, conversation_id: str, bot_output: BotOutput) -> MultiPostControlResponse:
        """Check the validation of bot's action

        Args:
            conversation_id (str): the id of the conversation
            bot_output (BotOutput): the action of the bot

        Returns:
            MultiPostControlResponse: the response of the post control
        """
        url = f"{self.url}/multi_post_control/{conversation_id}"
        response = requests.post(url, json=bot_output.model_dump())
        if response.status_code == 200:
            res = MultiPostControlResponse(**response.json())
            if not res.success:  # TODO: can add system instruction every turn?
                self.conv.add_message(res.msg)
            return res
        else:
            raise NotImplementedError

    def multi_tool_workflow(self, conversation_id: str, bot_output: BotOutput) -> MultiToolWorkflowResponse:
        """Get the response of the tool

        Args:
            conversation_id (str): the id of the conversation
            bot_output (BotOutput): the action of the bot

        Returns:
            MultiToolResponse: the response of the tool
        """
        url = f"{self.url}/multi_tool_workflow/{conversation_id}"
        response = requests.post(url, json=bot_output.model_dump())
        if response.status_code == 200:
            res = MultiToolWorkflowResponse(**response.json())
            self.conv.add_message(res.msg)
            return res
        else:
            raise NotImplementedError
