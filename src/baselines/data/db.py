""" updated @240906

"""
from typing import List
import pymongo, pymongo.results
from engine import Message, Conversation, Role

class DBManager:
    def __init__(self, uri='mongodb://localhost:27017/', db_name='message_database', collection_name='messages', **kwargs) -> None:
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_message(self, message: Message) -> pymongo.results.InsertOneResult:
        message_dict = message.to_dict()
        res = self.collection.insert_one(message_dict)
        # print(f"  <db> Inserted message: {message.content}")

    def insert_conversation(self, conversation: Conversation) -> pymongo.results.InsertManyResult:
        conversation_list = conversation.to_list()
        res = self.collection.insert_many(conversation_list)
        # print(f"  <db> Inserted conversation with {len(res.inserted_ids)} messages")
        return res

    def query_messages_by_conversation_id(self, conversation_id: str) -> Conversation:
        query = {"conversation_id": conversation_id}
        results = self.collection.find(query)
        messages = [Message(**{**res, "role": Role.get_by_rolename(res["role"])}) for res in results]
        return Conversation.from_messages(messages)
    
    def get_most_recent_unique_conversation_ids(self, num: int = 10) -> List[str]:
        pipeline = [
            {"$match": {"conversation_id": {"$ne": None}}},
            {"$group": {
                "_id": "$conversation_id",
                "latest_doc": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$latest_doc"}},
            {"$sort": {"conversation_id": -1}}, # _id
            {"$limit": num}
        ]
        results = self.collection.aggregate(pipeline)
        return [res["conversation_id"] for res in results]
        


if __name__ == "__main__":
    db_manager = DBManager(db_name="test_db", collection_name="messages")

    message = Message(role=Role.USER, content="Hello", prompt="prompt", llm_response="response", conversation_id="conv1", utterance_id=1)
    db_manager.insert_message(message)

    conversation = Conversation()
    conversation.msgs.append(message)
    conversation.msgs.append(Message(role=Role.SYSTEM, content="Hi there!", prompt="prompt", llm_response="response", conversation_id="conv1", utterance_id=2))
    db_manager.insert_conversation(conversation)

    messages = db_manager.query_messages_by_conversation_id("conv1")
    for msg in messages:
        print(msg.to_str())