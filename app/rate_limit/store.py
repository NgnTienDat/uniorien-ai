import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 1)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
)

WINDOW_SECONDS = 600  # 10 minutes


def get_used_tokens(key: str) -> int:
    value = redis_client.get(key)
    return int(value) if value else 0


def incr_tokens(key: str, amount: int) -> int:
    """
    Atomic increment token usage.
    If key is not set, set TTL
    """
    pipeline = redis_client.pipeline()
    pipeline.incrby(key, amount)
    pipeline.ttl(key)
    result = pipeline.execute()

    ttl = result[1]
    if ttl == -1:
        redis_client.expire(key, WINDOW_SECONDS)

    return result[0]
