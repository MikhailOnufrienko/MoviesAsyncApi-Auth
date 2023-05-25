import time

from redis import Redis

from ..settings import test_settings


if __name__ == '__main__':
    redis_client = Redis(host=test_settings.redis_host)

    while True:
        print('trying to access elastic redis')
        if redis_client.ping():
            break
        print('redis connection error')
        time.sleep(1)
