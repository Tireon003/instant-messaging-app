from typing import Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_server.repositories import ChatRepo, UserRepo
from api_server.services import ChatService, UserService


def get_user_service(get_async_session: Callable) -> Callable:
    def _get_user_service(
            session: AsyncSession = Depends(get_async_session)
    ) -> UserService:
        user_repo = UserRepo(session)
        return UserService(user_repo)
    return _get_user_service


def get_chat_service(get_async_session: Callable) -> Callable:
    def _get_chat_service(
            session: AsyncSession = Depends(get_async_session)
    ) -> ChatService:
        chat_repo = ChatRepo(session)
        return ChatService(chat_repo)
    return _get_chat_service

