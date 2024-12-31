import asyncio
from fa_core.common import init_loguru_logger, log_exceptions

logger = init_loguru_logger()


@log_exceptions()
def test_exception():
    logger.info("test exception")
    raise Exception("test exception")


@log_exceptions()
async def test_async_exception():
    logger.info("test async exception")
    raise Exception("test async exception")


if __name__ == "__main__":
    try:
        test_exception()
    except Exception as e:
        logger.error(f"test exception: {e}")
    try:
        asyncio.run(test_async_exception())
    except Exception as e:
        logger.error(f"test async exception: {e}")
