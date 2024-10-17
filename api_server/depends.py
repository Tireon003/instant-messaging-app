from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Annotated

from api_server.repositories import UserRepo
from api_server.services import UserService
from api_server.schemas import UserCredentials


def get_user_service(get_async_session: Callable) -> Callable:
    def _get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
        user_repo = UserRepo(session)
        return UserService(user_repo)
    return _get_user_service


def get_login_form(credentials: Annotated[UserCredentials, Depends(OAuth2PasswordRequestForm)]):
    data = UserCredentials(
        username=credentials.username,
        password=credentials.password
    )
    return data
