"""
@241209
- [x] basic implement
@241210
- [x] post_control
@241211
- [x] add log (to db) -> backend
- [x] multi-agent

todos
- [ ]
"""

import json
from typing import Dict, Iterator

import requests
from loguru import logger

from fa_core.common import Config
from fa_core.data import BotOutput, Conversation, Role

from ..typings import (
    SingleBotPredictResponse,
    SinglePostControlResponse,
    SingleRegisterRequest,
    SingleRegisterResponse,
    SingleToolResponse,
)
from .client_base import BaseClient


class SingleAgentMixin(BaseClient):
    """Wrapper of `backend/routers/router_single_agent.py`

    NOTE:
    - The conversation should be synced with the backend! So note to `add_message`!

    Usage::

        # see `test/backend/test_ui_backend_single.py`
        client = FrontendClient(cfg.backend_url)
        # 1. init the conversation
        _ = client.single_register(conversation_id, cfg)
        # 2. query loop
        while True:
            client.single_user_input(conversation_id, user_input)
            while True:
                stream = client.single_bot_predict(conversation_id)  # process the Iterator
                res_bot_predict = client.single_bot_predict_output(conversation_id)
                bot_output = res_bot_predict.bot_output
                if bot_output.action:
                    res_post_control = client.single_post_control(conversation_id, bot_output)
                    if not res_post_control.success:
                        continue
                    res_tool = client.single_tool(conversation_id, bot_output)
                elif bot_output.response:
                    break
        # 3. disconnect
        client.single_disconnect(conversation_id)
    """

    def single_register(self, conversation_id: str, config: Config, user_identity: Dict = None) -> Conversation:
        """Register a new conversation

        Args:
            conversation_id (str): the id of the conversation
            config (Config): the config of the conversation
        """
        url = f"{self.url}/single_register/{conversation_id}"
        response = requests.post(
            url,
            json=SingleRegisterRequest(user_identity=user_identity, config=config).model_dump(),
        )
        if response.status_code == 200:
            result = SingleRegisterResponse(**response.json())
            self.pdl_str = result.pdl_str
            self.procedure_str = result.procedure_str
            self.conv = result.conversation
            return self.conv
        else:
            logger.error(f"Error: {response.text}")
            raise NotImplementedError

    def single_disconnect(self, conversation_id: str):
        url = f"{self.url}/single_disconnect/{conversation_id}"
        response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise NotImplementedError

    def single_user_input(self, conversation_id: str, query: str):
        """Add a user message to the conversation

        Args:
            conversation_id (str): the id of the conversation
            query (str): the message of the user
        """
        self.conv.add_message(query, role=Role.USER)
        url = f"{self.url}/single_add_message/{conversation_id}"
        response = requests.post(url, json=self.conv.get_last_message().model_dump())
        if response.status_code == 200:
            return response.json()
        else:
            raise NotImplementedError

    def single_bot_predict(self, conversation_id: str) -> Iterator[str]:
        """Get the response of the bot in stream (step 1)

        Args:
            conversation_id (str): the id of the conversation

        Returns:
            Iterator[str]: the response of the bot
        """
        logger.info(f">> single_bot_predict with conversation: {json.dumps(str(self.conv), ensure_ascii=False)}")
        url = f"{self.url}/single_bot_predict/{conversation_id}"
        return self.process_stream_url(url)

    def single_bot_predict_output(self, conversation_id: str) -> SingleBotPredictResponse:
        """Get the response of the bot (step 2)

        Args:
            conversation_id (str): the id of the conversation

        Returns:
            SingleBotPredictResponse: the response of the bot
        """
        url = f"{self.url}/single_bot_predict_output/{conversation_id}"
        response = requests.get(url)
        if response.status_code == 200:
            res = SingleBotPredictResponse(**response.json())
            # add message to sync with backend!
            self.conv.add_message(res.msg, role=Role.BOT)
            return res
        else:
            logger.error(f"Error: {response.text}")
            raise NotImplementedError

    def single_post_control(self, conversation_id: str, bot_output: BotOutput) -> SinglePostControlResponse:
        """Check the validation of bot's action

        Args:
            conversation_id (str): the id of the conversation
            bot_output (BotOutput): the action of the bot

        Returns:
            SinglePostControlResponse: the response of the post control
        """
        url = f"{self.url}/single_post_control/{conversation_id}"
        response = requests.post(url, json=bot_output.model_dump())
        if response.status_code == 200:
            res = SinglePostControlResponse(**response.json())
            if not res.success:
                self.conv.add_message(res.msg, role=Role.SYSTEM)
            return res
        else:
            raise NotImplementedError

    def single_tool(self, conversation_id: str, bot_output: BotOutput) -> SingleToolResponse:
        """Get the response of the tool

        Args:
            conversation_id (str): the id of the conversation
            bot_output (BotOutput): the action of the bot

        Returns:
            SingleToolResponse: the response of the tool
        """
        url = f"{self.url}/single_tool/{conversation_id}"
        response = requests.post(url, json=bot_output.model_dump())
        if response.status_code == 200:
            res = SingleToolResponse(**response.json())
            self.conv.add_message(res.msg, role=Role.SYSTEM)
            return res
        else:
            raise NotImplementedError
