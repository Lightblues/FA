import json
import datetime

json_line = lambda x: json.dumps(x, ensure_ascii=False)


def get_session_id():
    # "%Y-%m-%d %H:%M:%S.%f"
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
