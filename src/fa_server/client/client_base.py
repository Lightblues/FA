import json
import time
from typing import Iterator

import requests

from fa_core.common import Config
from fa_core.data import Conversation
from pydantic import BaseModel, ConfigDict


class BaseClient(BaseModel):
    """Base client class for frontend-backend communication"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    backend_url: str = None

    conv: Conversation = None  # the conversation that sync with backend
    pdl_str: str = None  # the pdl that sync with backend
    procedure_str: str = None

    def process_stream_url(self, url: str, data: dict = None) -> Iterator[str]:
        """Process the stream url and return the iterator of the stream

        Args:
            url (str): The stream URL to process
            data (dict, optional): The data to send in POST request. Defaults to None.
        """
        headers = {"Accept": "text/event-stream"}
        max_retries = 3
        retry_count = 0
        backoff_time = 1  # Initial backoff time in seconds

        while retry_count < max_retries:
            try:
                with requests.post(url, headers=headers, json=data, stream=True) as response:
                    if response.status_code != 200:
                        print(f"Error: {response.text}")
                        raise NotImplementedError

                    for line in response.iter_lines():
                        if not line:
                            continue

                        try:
                            decoded_line = line.decode("utf-8").strip()
                            if decoded_line.startswith("data:"):
                                json_data = decoded_line[len("data:") :].strip()
                                data = json.loads(json_data)
                                yield data["chunk"]
                        except (json.JSONDecodeError, UnicodeDecodeError) as e:
                            print(f"Error processing line: {e}")
                            continue

                    break  # Successfully completed

            except (requests.exceptions.ChunkedEncodingError, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Failed after {max_retries} retries: {str(e)}")

                print(f"Connection error (attempt {retry_count}/{max_retries}): {str(e)}")
                time.sleep(backoff_time)
                backoff_time *= 2  # Exponential backoff
