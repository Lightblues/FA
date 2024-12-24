"""
# db.ui_single_sessions | ui_multi_sessions
_session_info = {
    # model_llm_name, template, etc
    "session_id": ss.conv.conversation_id,
    "user": ss.user_identity,
    "mode": ss.mode,            # "single"
    "conversation": ss.conv.to_list(),
    "config": ss.cfg.model_dump(),
}
"""

from typing import *

import pymongo
import pymongo.results

from fa_core.common import Config
from fa_core.data import Conversation, Message


class DBUtils:
    def __init__(self, mongo_uri="mongodb://localhost:27017", db_name="agent-pdl"):
        self.db = pymongo.MongoClient(mongo_uri)[db_name]

    def find_one_by_sessionid(self, session_id: str, collection: str = "ui_multi_sessions") -> Any:
        """find_one by session_id"""
        return self.db[collection].find_one({"session_id": session_id})

    def get_data_by_sessionid(self, session_id: str, collection: str = "ui_multi_sessions") -> Tuple[Config, Conversation]:
        """get conversation by session_id"""
        doc = self.find_one_by_sessionid(session_id, collection)
        if not doc:
            return None

        # 从数据库文档中重建 Config, Conversation 对象
        config = Config(**doc["config"])

        messages = [Message(**msg) for msg in doc["conversation"]]
        conv = Conversation.from_messages(messages)
        return config, conv

    def get_latest_sessionids(self, n: int = 10, collection: str = "ui_multi_sessions") -> List[str]:
        return [doc["session_id"] for doc in self.db[collection].find().sort("session_id", pymongo.DESCENDING).limit(n)]
