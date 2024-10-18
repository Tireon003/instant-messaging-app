from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Annotated

from api_server.repositories import UserRepo, ChatRepo
from api_server.services import UserService, ChatService
from api_server.schemas import UserCredentials, TokenPayload
from api_server.utils import JwtTool

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_token_payload(
        access_token: Annotated[str, Depends(oauth2_scheme)]
) -> TokenPayload:
    payload_dict = JwtTool.read_token(access_token)
    payload_schema = TokenPayload.model_validate(payload_dict)
    return payload_schema


def get_user_service(get_async_session: Callable) -> Callable:
    def _get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
        user_repo = UserRepo(session)
        return UserService(user_repo)
    return _get_user_service


def get_chat_service(get_async_session: Callable) -> Callable:
    def _get_chat_service(session: AsyncSession = Depends(get_async_session)) -> ChatService:
        chat_repo = ChatRepo(session)
        return ChatService(chat_repo)
    return _get_chat_service


def get_login_form(credentials: Annotated[UserCredentials, Depends(OAuth2PasswordRequestForm)]):
    data = UserCredentials(
        username=credentials.username,
        password=credentials.password
    )
    return data
