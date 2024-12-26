import json
import datetime
import uuid

json_line = lambda x: json.dumps(x, ensure_ascii=False)


def get_session_id():
    # "%Y-%m-%d %H:%M:%S.%f"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    # NOTE: use uuid4 to avoid collision
    hash_suffix = str(uuid.uuid4())[:8]
    return f"{timestamp}_{hash_suffix}"
