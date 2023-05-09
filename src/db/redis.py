from redis.asyncio import Redis

redis: Redis = Redis()


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis
