from redis.asyncio import Redis, from_url


async def get_redis(host: str, port: int, db_num: int) -> Redis:
    redis = from_url(f"redis://{host}:{port}/{db_num}")
    redis.ping()
    return redis
