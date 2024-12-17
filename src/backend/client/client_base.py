import json, requests
from typing import Iterator
from flowagent.data import Conversation, Config


class BaseClient:
    """Base client class for frontend-backend communication"""
    
    url: str = None
    conv: Conversation = None       # the conversation that sync with backend
    pdl_str: str = None            # the pdl that sync with backend

    def __init__(self, config: Config):
        self.url = config.backend_url

    def process_stream_url(self, url: str, data: dict = None) -> Iterator[str]:
        """Process the stream url and return the iterator of the stream
        
        Args:
            url (str): The stream URL to process
            data (dict, optional): The data to send in POST request. Defaults to None.
        
        NOTE: only use streaming, no async!
        """
        headers = {'Accept': 'text/event-stream'}
        response = requests.post(url, headers=headers, json=data, stream=True)
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
