import logging
import time
from functools import wraps

from utils.logging_settings import setup_logging

setup_logging()


def backoff(
        start_time: float = 0.1,
        factor: int = 2,
        border_time: int = 10) -> callable:
    """
    Function for repeatable execution of a function if error appears.

    Formula:
        t = start_time * 2^(n) if t < border_time
        t = start_time if t >= border_time
    :param start_time: start sleep time for repetition
    :param factor: sleep time multiplication factor
    :param border_time: border sleep time for repetition
    :return: function execution result
    """

    def func_wrapper(func: callable) -> callable:

        @wraps(func)
        def inner(*args, **kwargs) -> callable:
            """Function Body."""

            attempts = 0

            while True:
                sleep_time = min(border_time, start_time * factor ** attempts)

                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    attempts += 1
                    logging.error('Could not connect: %s', exc)
                    time.sleep(sleep_time)

        return inner

    return func_wrapper
