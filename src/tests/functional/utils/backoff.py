import logging
import time
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)


def backoff(
        exception,
        start_sleep_time: float = 0.1,
        factor: int = 2,
        border_sleep_time: int = 30,
        max_attempts: int = 10
) -> Callable:
    """
    A function to execute the function again after some time,
    if an error has occurred. Uses a naive exponential growth
    of the repetition time (factor) to the border_sleep_time.

    The formula is:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param exception: an exception arising when connection failed
    :param start_sleep_time: the initial repetition time
    :param factor: how many times to increase the wait time
    :param border_sleep_time: boundary wait time
    :param max_attempts: maximum of connection attempts
    :return: result of function execution
    """

    def func_wrapper(func):

        @wraps(func)
        def inner(*args, **kwargs):
            """Function Body."""

            attempts = 0

            while True:
                sleep_time = min(
                    border_sleep_time, start_sleep_time * factor ** attempts
                )

                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if attempts == max_attempts:
                        raise exc

                    attempts += 1
                    logger.error('Error message: %s', exc)
                    logger.warning(
                        'Waiting for %s seconds, then a new attempt',
                        sleep_time
                    )
                    time.sleep(sleep_time)

        return inner

    return func_wrapper
