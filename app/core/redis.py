from redis.asyncio import Redis


async def get_redis(host: str, port: int, db_num: int) -> Redis:
    redis = Redis.from_url(
        f"redis://{host}:{port}/{db_num}", decode_responses=True, max_connections=20
    )
    await redis.ping()  # type: ignore
    return redis
