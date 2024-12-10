""" 
@241209
- [x] basic implement

- [ ] add log (to db)
- [ ] post_control
- [ ] multi-agent
"""
import requests, json, asyncio, aiohttp
from typing import Union, Iterator, Tuple, AsyncIterator
from flowagent.data import Config, DataManager, Conversation, BotOutput, APIOutput
from .typings import (
    SingleRegisterResponse, 
    SingleBotPredictRequest, SingleBotPredictResponse, 
    SinglePostControlResponse, 
    SingleToolResponse
)
# SingleBotPredictRequest, SinglePostControlResponse

class FrontendClient:
    """Wrapper of `ui_backend.single_agent`

    Usage::

        client = FrontendClient()
        conv = client.single_register(conversation_id, cfg)
        stream = client.single_bot_predict(conversation_id, conv)
        # process the Iterator
        bot_output = client.single_bot_predict_output(conversation_id)
    """
    def __init__(self, url: str="http://localhost:8100"):
        self.url = url

    def single_register(self, conversation_id: str, config: Config) -> SingleRegisterResponse:
        url = f"{self.url}/single_register/{conversation_id}"
        response = requests.post(url, json=config.model_dump())
        if response.status_code == 200:
            result = response.json()
            conv = result["conversation"]
            conv = Conversation.load_from_json(conv)
            return conv
        else: 
            print(f"Error: {response.text}")
            raise NotImplementedError

    def single_bot_predict(self, conversation_id: str, query: str) -> Iterator[str]:
        url = f"{self.url}/single_bot_predict/{conversation_id}"
        headers = {'Accept': 'text/event-stream'}
        # NOTE: only use streaming, no async!
        response = requests.post(url, json=SingleBotPredictRequest(**{"query": query}).model_dump(), headers=headers, stream=True)
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            raise NotImplementedError
        for line in response.iter_lines():
            if line:
                # Decode the line and strip the prefix
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith("data:"):
                    json_data = decoded_line[len("data:"):].strip()
                    try:
                        data = json.loads(json_data)  # Parse the JSON
                        yield data['chunk']
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")

    def single_bot_predict_output(self, conversation_id: str) -> SingleBotPredictResponse:
        url = f"{self.url}/single_bot_predict_output/{conversation_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return SingleBotPredictResponse(**response.json())
        else: 
            print(f"Error: {response.text}")
            raise NotImplementedError

    def single_post_control(self, conversation_id: str, bot_output: BotOutput) -> SinglePostControlResponse:
        url = f"{self.url}/single_post_control/{conversation_id}"
        response = requests.post(url, json=bot_output.model_dump())
        if response.status_code == 200:
            return SinglePostControlResponse(**response.json())
        else: raise NotImplementedError

    def single_tool(self, conversation_id: str, bot_output: BotOutput) -> SingleToolResponse:
        url = f"{self.url}/single_tool/{conversation_id}"
        response = requests.post(url, json=bot_output.model_dump())
        if response.status_code == 200:
            return SingleToolResponse(**response.json())
        else: raise NotImplementedError


if __name__ == '__main__':
    client = FrontendClient()
    conversation_id = "xxx"
    cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    conv = client.single_register(conversation_id, cfg)
    bot_output = client.single_bot_predict(conversation_id, conv)
    print()