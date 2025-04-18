from typing import AsyncGenerator
from uuid import UUID

from redis.asyncio import ConnectionPool, Redis

from settings import settings
from models import Secret


pool = ConnectionPool.from_url(
    url=f"redis://{settings.REDIS_USER}:{settings.REDIS_PASSWORD}@redis",
    decode_responses=True,
    max_connections=10
)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    async with Redis.from_pool(pool) as client:
        yield client


async def create_secret_in_cache(client: Redis, secret_key: UUID, secret: Secret):
    secret_key = str(secret.secret_key)

    await client.hset(
        secret_key,
        mapping={
            'secret_key': secret_key,
            'secret': secret.secret,
            'ttl_seconds': secret.ttl_seconds,
            'is_accessed': str(secret.is_accessed),
            'created_at': str(secret.created_at)
        },
    )
    await client.expire(secret_key, settings.REDIS_EXPIRE_TIME)


async def get_secret_from_cache(client: Redis, secret_key: UUID):
    try:
        secret = await client.hgetall(str(secret_key))
    except TypeError:
        return False
    return secret


async def delete_secret_from_cache(client: Redis, secret_key: UUID):
    await client.delete(str(secret_key))
