import logging
from collections.abc import AsyncIterator
from typing import AsyncGenerator

from redis import asyncio as aioredis
from redis.asyncio import Redis as RedisInstance
from contextlib import asynccontextmanager

from api_server.config import settings


logger = logging.getLogger(__name__)


class Redis:

    REDIS_URL = settings.redis_url

    @asynccontextmanager
    async def create_connection(self) -> AsyncIterator[RedisInstance]:
        connection = await aioredis.from_url(self.REDIS_URL)  # type: ignore
        yield connection
        await connection.close()

    async def get_connection(self) -> RedisInstance:
        try:
            async with self.create_connection() as connection:
                logger.info("Created redis connection.")
                return connection
        except aioredis.ConnectionError as e:
            logger.error("Error while connecting to redis: %s", e)
