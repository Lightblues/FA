
# %%
from flowagent.data import DBManager, Conversation, Message, Role
db = DBManager(db_name="pdl", collection_name="messages")
res = db.query_messages_by_conversation_id('2024-09-25 14:30:45.207180')
res[1].to_dict()

# %%
df = res.to_dataframe()

# %%
conv = Conversation()
conv.add_message(Message(
    Role.USER, "hello",
    conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id
))
# %%
conv.to_list()
# %%
conv.conversation_id
# %%
db.insert_conversation(conv)
# %%
res = db.query_messages_by_conversation_id(conv.conversation_id)

# %%
res[0].utterance_id



# %%
import json
from flowagent.data.base_data import Message, Conversation
with open("/work/huabu/dataset/STAR/user_profile_w_conversation/000.json", 'r') as f:
    d = json.load(f)
conv = Conversation.load_from_json(d[0]["conversation"])
conv
# %%
conv.get_message_by_idx(13).apis
# %%
