import pymongo

from fa_server.common import check_db_connection
from fa_core.common import Config, DBUtils


def test_db_connection():
    config = Config.from_yaml("default.yaml")
    client = pymongo.MongoClient(config.db_uri)
    if not check_db_connection(client):
        print("Database connection failed")
        return None
    else:
        print("Database connection successful")
        return client


def test_db_utils():
    cfg = Config.from_yaml("default.yaml")
    db_utils = DBUtils(mongo_uri=cfg.db_uri, db_name=cfg.db_name)
    print(db_utils.get_exp_versions(collection="dev_single_sessions"))
    print()


# client = test_db_connection()
test_db_utils()
