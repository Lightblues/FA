# %%
from flowagent.data.db import DBManager
db = DBManager(db_name="pdl", collection_name="messages", meta_collection_name="config")
# %%
db.get_most_recent_unique_conversation_ids(limit=10)

# %%
coll = db.collection_meta
list(coll.find())
# %%
d = {
    "a": 1,
    "b": 2,
    **{
        "c": 3,
        "b": 4
    }
}
d
# %%
