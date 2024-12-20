from common import init_loguru_logger, log_exceptions

logger = init_loguru_logger()


@log_exceptions()
def test_exception():
    logger.info("test exception")
    raise Exception("test exception")


if __name__ == "__main__":
    test_exception()
