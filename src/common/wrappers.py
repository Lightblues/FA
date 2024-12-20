import functools
import time
import traceback
from typing import Callable
from loguru import logger


class Timer:
    """timer of a function
    USAGE:
        with Timer("func_name", print=True):
            func()
    """

    def __init__(self, name, print=True):
        self.name = name
        self.print = print

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        if self.print:
            print(f"  <timer> {self.name} took {self.elapsed_time:.4f} seconds")


def retry_wrapper(retry: int = 3, step_name: str = "", log_fn: Callable = print):
    """retry `retry` times for a function

    USAGE::
        @retry_wrapper(retry=3, step_name="example_function", log_fn=xxx)
        def example_function(xxx):
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            for _retry in range(retry):
                try:
                    res = f(*args, **kwargs)
                    return res
                except Exception as e:
                    log_fn(f"<{step_name}> [retry {_retry}/{retry}] encountered error: {e}")
                    log_fn(f"  >>> traceback\n" + traceback.format_exc())
            else:
                raise Exception(f"<{step_name}> failed for {retry} times!!! \n  Args: {args}, Kwargs: {kwargs}")

        return wrapped_f

    return decorator


def log_exceptions():
    """Log exceptions using logger.error(...)

    USAGE::
        @log_exceptions()
        def example_function(xxx):
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {f.__name__}: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                raise

        return wrapped_f

    return decorator
