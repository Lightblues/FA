from flowagent.ui_conv.util_db import *

session_id = "2024-12-05 20:12:44.472982"

config, conv = get_data_by_sessionid(session_id)
print(conv)
