# %%
conversation_s = """[BOT] 你好，我是000-114挂号机器人，有什么可以帮您?
[USER] 你好，我想挂一个病理科的号，能帮我查一下有哪些医院可以挂号吗？
[BOT] 当然可以帮您查询。请问您想在哪家医院挂号呢？
[USER] 我还没决定具体哪家医院。你能推荐一些在病理科方面比较有名的医院吗？
[BOT] 好的，针对病理科，我们可以推荐一些专业的医院。请问您有特定的时间想要挂号吗？
[USER] 我希望尽快挂号，最好是这周内的号。
[BOT] <Call API> 其他医院号源推荐(['keshi_name', 't_time'])
[SYSTEM] Entity linked! Actually called API: 其他医院号源推荐(['keshi_name', 't_time'])
<API response> {'error_code': 0, 'error_message': None, 'response': [{'num': 5, 'hos_name': '北京协和医院', 'doc_name': '张医生'}, {'num': 3, 'hos_name': '上海瑞金医院', 'doc_name': '李医生'}, {'num': 4, 'hos_name': '广州中山大学附属第一医院', 'doc_name': '王医生'}]}"""


from engine import Conversation
conv = Conversation.load_from_str(conversation_s)
conv
# %%
from easonsi.llm.openai_client import OpenAIClient
from engine.common import init_client, LLM_CFG
client = init_client(llm_cfg=LLM_CFG["custom"])
client.query_one_stream("请问您有特定的时间想要挂号吗？")
# %%
import yaml
s = """available_models: 
- null
sxx: ff
"""
data = yaml.safe_load(s)
data
# %%
