import json, requests
from typing import Iterator
from flowagent.data import Conversation


class BaseClient:
    """Base client class for frontend-backend communication"""
    
    url: str = "http://9.134.230.111:8100"
    conv: Conversation = None       # the conversation that sync with backend
    pdl_str: str = None            # the pdl that sync with backend

    def __init__(self, url: str="http://9.134.230.111:8100"):
        self.url = url

    def process_stream_url(self, url: str) -> Iterator[str]:
        headers = {'Accept': 'text/event-stream'}
        # NOTE: only use streaming, no async!
        response = requests.post(url, headers=headers, stream=True)
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