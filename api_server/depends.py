from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from api_server.repositories import UserRepo
from api_server.services import UserService


def get_user_service(get_async_session: Callable) -> Callable:
    def _get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
        user_repo = UserRepo(session)
        return UserService(user_repo)
    return _get_user_service
