import time

from redis import ConnectionError, Redis

from src.tests.functional.utils.backoff import backoff
from src.tests.functional.settings import test_settings


@backoff(ConnectionError)
def check_redis_conn(client: Redis):
    if not client.ping():
        raise ConnectionError


if __name__ == '__main__':
    redis_client = Redis(host=test_settings.redis_host)
    check_redis_conn(redis_client)
