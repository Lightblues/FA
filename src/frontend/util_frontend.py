from typing import List, Dict, Iterator
import time

def fake_stream(response: str) -> Iterator[str]:
    for chunk in response:
        yield chunk
        time.sleep(0.02)

