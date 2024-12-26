import pymongo

from fa_demo.backend.common.shared import check_db_connection
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
    db_utils = DBUtils()
    print(db_utils.get_exp_versions(collection="dev_single_sessions"))
    print()


# client = test_db_connection()
test_db_utils()
