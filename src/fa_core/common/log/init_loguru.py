import os
import sys
from pathlib import Path

from loguru import logger
from loguru._logger import Logger

DIR_default_log = Path(__file__).resolve().parent.parent.parent.parent.parent / "log/default"


def singleton(func):
    """Decorator to ensure function is only called once"""
    func._initialized = False

    def wrapper(*args, **kwargs):
        if not func._initialized:
            func._initialized = True
            return func(*args, **kwargs)
        return logger  # Return existing logger instance

    return wrapper


@singleton
def init_loguru_logger(log_dir=DIR_default_log, stdout_level="INFO") -> "Logger":
    """initialize the loguru logger

    Args:
        log_dir (str, optional): the directory to save the log files.

    Returns:
        Logger: loguru.logger

    Examples::

        logger = init_loguru_logger()
        logger.info("logging to main log")
        logger.bind(custom=True).debug("logging to custom log")

        # in other file, can directly import logger
        from loguru import logger

        logger.info("xxx")

    """
    os.makedirs(log_dir, exist_ok=True)
    # print(f"<init_loguru_logger> logging to {log_dir}")

    logger.remove()
    logger.add(
        f"{log_dir}/custom_debug.log",
        rotation="10 MB",
        compression="zip",
        level="DEBUG",
        filter=lambda record: "custom" in record["extra"],
    )
    logger.add(f"{log_dir}/app.log", rotation="10 MB", compression="zip", level="INFO")
    logger.add(sys.stdout, level=stdout_level)
    return logger


def set_log_level(level: str):
    logger.level(level)


def get_log_level():
    return logger.level
