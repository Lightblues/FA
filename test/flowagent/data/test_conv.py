
# %%
from flowagent.data import DBManager, Conversation, Message, Role

# db = DBManager(db_name="pdl", collection_name="messages")
# res = db.query_messages_by_conversation_id('2024-09-25 14:30:45.207180')
# res[1].to_dict()
# df = res.to_dataframe()

def test_add_message():
    conv = Conversation()
    conv.add_message(Message(
        role=Role.USER, content="hello",
        conversation_id=conv.conversation_id, utterance_id=conv.current_utterance_id
    ))
    conv.add_message(msg="hello", role=Role.USER)
    print(conv)
    print()


test_add_message()

