import aioredis
from aioredis.client import Redis

from api_server.config import settings


class Redis:

    URL = settings.redis_url

    @classmethod
    async def create_redis_connection(cls) -> Redis:
        conn = await aioredis.from_url(cls.URL)
        yield conn
