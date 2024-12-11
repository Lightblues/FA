import pymongo, loguru
from loguru._logger import Logger
from flowagent.data import Config, init_loguru_logger, DataManager

class SharedResources:
    _instance = None
    
    def __init__(self, config: Config):
        self.config = config
        self.db = pymongo.MongoClient(config.db_uri)[config.db_name]
        self.logger = init_loguru_logger(DataManager.DIR_backend_log)
    
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

# 创建便捷的访问方法
def get_db() -> pymongo.MongoClient:
    return SharedResources.get_instance().db

def get_logger() -> Logger:
    return SharedResources.get_instance().logger
