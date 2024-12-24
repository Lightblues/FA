import json
import time
from typing import Iterator

import requests

from fa_core.common import Config
from fa_core.data import Conversation


class BaseClient:
    """Base client class for frontend-backend communication"""

    url: str = None
    conv: Conversation = None  # the conversation that sync with backend
    pdl_str: str = None  # the pdl that sync with backend

    def __init__(self, config: Config):
        self.url = config.backend_url

    def process_stream_url(self, url: str, data: dict = None) -> Iterator[str]:
        """Process the stream url and return the iterator of the stream

        Args:
            url (str): The stream URL to process
            data (dict, optional): The data to send in POST request. Defaults to None.
        """
        headers = {"Accept": "text/event-stream"}
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = requests.post(url, headers=headers, json=data, stream=True)
                if response.status_code != 200:
                    print(f"Error: {response.text}")
                    raise NotImplementedError

                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        # Decode the line and strip the prefix
                        decoded_line = line.decode("utf-8").strip()
                        if decoded_line.startswith("data:"):
                            json_data = decoded_line[len("data:") :].strip()
                            data = json.loads(json_data)
                            yield data["chunk"]
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"Error processing line: {e}")
                        continue

                # 如果成功完成，跳出重试循环
                break

            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError) as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Failed after {max_retries} retries: {str(e)}")
                print(f"Connection error (attempt {retry_count}/{max_retries}): {str(e)}")
                time.sleep(1)  # 重试前等待1秒
