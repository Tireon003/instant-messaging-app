import logging
from typing import AsyncGenerator

from redis import asyncio as aioredis
from redis.asyncio import Redis as RedisInstance
from contextlib import asynccontextmanager

from api_server.config import settings

logger = logging.getLogger(__name__)


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
                logger.info("Created redis connection.")
                return conn
        except aioredis.ConnectionError as e:
            logger.error("Error while connecting to redis: %s", e)
