import requests, json
from sseclient import SSEClient
from flowagent.data import Config, DataManager, Conversation

class FrontendClient:
    def __init__(self, url: str="http://localhost:8100"):
        self.url = url

    def single_register(self, conversation_id: str, config: Config) -> Conversation:
        url = f"{self.url}/single_register/{conversation_id}"
        response = requests.post(url, json=config.model_dump())
        if response.status_code == 200:
            result = response.json()
            conv = result["conversation"]
            conv = Conversation.load_from_json(conv['msgs'])
            return conv
        else: raise NotImplementedError

    def single_bot_predict(self, conversation_id: str, conv: Conversation):
        url = f"{self.url}/single_bot_predict/{conversation_id}"
        response = requests.post(
            url, 
            json=conv.model_dump(),
            stream=True, headers={'Accept': 'text/event-stream'}
        )

        sse_client = SSEClient(response)
        for event in sse_client.events():
            data = json.loads(event.data)
            if data['is_finish']:
                print(f"\n\n{data['bot_output']}\n\n")
            else:
                print(data['chunk'], end="")
        return data

client = FrontendClient()
conversation_id = "xxx"
cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
conv = client.single_register(conversation_id, cfg)
bot_output = client.single_bot_predict(conversation_id, conv)
print()