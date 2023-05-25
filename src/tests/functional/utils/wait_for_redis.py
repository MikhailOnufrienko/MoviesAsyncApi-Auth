import time

from redis import Redis


if __name__ == '__main__':
    redis_client = Redis(host='redis', port=6379)

    while True:
        print('trying to access elastic redis')
        if redis_client.ping():
            break
        print('redis connection error')
        time.sleep(1)
