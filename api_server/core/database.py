from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from api_server.config import settings


class Database:

    def __init__(self) -> None:
        self.__engine = create_async_engine(url=settings.db_url, echo=True)
        self.__session_maker = async_sessionmaker(
            self.__engine, expire_on_commit=False
        )

    @asynccontextmanager
    async def create_async_session(self) -> AsyncIterator[AsyncSession]:
        async with self.__session_maker() as session:
            yield session

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        try:
            async with self.create_async_session() as session:
                yield session
        except Exception as e:
            await session.rollback()
            raise e


database = Database()
