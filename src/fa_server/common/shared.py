"""
- [ ] #debug skip `db` operations for debuging
"""

from typing import Union

import pymongo
from loguru import logger
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from fa_core.common import Config


def check_db_connection(client: MongoClient) -> bool:
    """Check if MongoDB client connection is available

    Args:
        client: MongoDB client instance
    Returns:
        bool: True if connected, False otherwise
    """
    try:
        # Ping the database
        client.admin.command("ping")
        return True
    except Exception as e:
        logger.warning(f"MongoDB client {client} connection failed: {e}")
        return False


class SharedResources:
    _instance = None
    db_client: MongoClient = None
    db: Database = None

    def __init__(self, config: Config):
        self.config = config
        logger.info(f"Connecting to MongoDB with URI: {config.db_uri}, DB: {config.db_name}")
        self.db_client = pymongo.MongoClient(config.db_uri)
        if not check_db_connection(self.db_client):
            logger.error(f"Failed to connect to MongoDB with URI: {config.db_uri}")
            self.db_client = None
        else:
            self.db = self.db_client[config.db_name]

    @classmethod
    def initialize(cls, config: Config):
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("SharedResources not initialized")
        return cls._instance


def get_db() -> Union[Database, None]:
    return SharedResources.get_instance().db
