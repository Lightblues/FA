import pymongo

from backend.common.shared import check_db_connection
from flowagent.data import Config, DataManager


def test_db_connection():
    config = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
    client = pymongo.MongoClient(config.db_uri)
    if not check_db_connection(client):
        print("Database connection failed")
        return None
    else:
        print("Database connection successful")
        return client


client = test_db_connection()
print()
