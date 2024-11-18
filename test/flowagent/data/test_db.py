from flowagent.data.db import DBManager
db = DBManager(db_name="pdl", collection_name="messages", meta_collection_name="config")


most_recent_conv_ids = db.get_most_recent_unique_conversation_ids(limit=10)
print(f"most_recent_conv_ids: {most_recent_conv_ids}")

# coll = db.collection_meta
# list(coll.find())
