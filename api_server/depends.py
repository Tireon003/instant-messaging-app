from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from api_server.repositories import UserRepo


def get_user_repository(get_async_session: Callable) -> Callable:
    def _get_user_repository(session: AsyncSession = Depends(get_async_session)) -> UserRepo:
        return UserRepo(session)

    return _get_user_repository
