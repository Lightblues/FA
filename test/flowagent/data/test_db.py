from flowagent.data.db import DBManager
from flowagent.data import Role, Message, Conversation
db_manager = DBManager(db_name="pdl", collection_name="messages", meta_collection_name="config")

def test_get_recent_conversation_ids():
    most_recent_conv_ids = db_manager.get_most_recent_unique_conversation_ids(limit=10)
    print(f"most_recent_conv_ids: {most_recent_conv_ids}")

def test_message():
    message = Message(role=Role.USER, content="Hello", prompt="prompt", llm_response="response", conversation_id="conv1", utterance_id=1)
    db_manager.insert_message(message)

    conversation = Conversation()
    conversation.msgs.append(message)
    conversation.msgs.append(Message(role=Role.SYSTEM, content="Hi there!", prompt="prompt", llm_response="response", conversation_id="conv1", utterance_id=2))
    db_manager.insert_conversation(conversation)

    messages = db_manager.query_messages_by_conversation_id("conv1")
    for msg in messages:
        print(msg.to_str())

