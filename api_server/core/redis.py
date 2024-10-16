from typing import AsyncGenerator

from redis import asyncio as aioredis
from redis.asyncio import Redis as RedisInstance
from contextlib import asynccontextmanager

from api_server.config import settings


class Redis:

    URL = settings.redis_url

    @asynccontextmanager
    async def create_connection(self) -> AsyncGenerator[RedisInstance, None]:
        conn = await aioredis.from_url(self.URL)
        yield conn
        await conn.close()

    async def get_connection(self) -> RedisInstance:
        try:
            async with self.create_connection() as conn:
                return conn
        except aioredis.ConnectionError as e:
            print(f"Redis connection error: {e}")
