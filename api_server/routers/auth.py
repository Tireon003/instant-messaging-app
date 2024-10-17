from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
    Response,
)
from fastapi.responses import (
    JSONResponse,
)
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import timedelta

from api_server.schemas import UserLogin, UserSignup
from api_server.services import UserService
from api_server.depends import get_user_service, get_login_form
from api_server.core import database

router = APIRouter(
    prefix='/api/auth',
    tags=['auth'],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
        user_login_data: Annotated[UserLogin, Depends(get_login_form)],
        service: Annotated[UserService, Depends(get_user_service(database.get_async_session))],
) -> JSONResponse:
    token = await service.login_user(user_data=user_login_data)
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": token,
            "token_type": "Bearer",
        }
    )
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=timedelta(days=1).days * 86400,
    )
    return response


@router.post("/generate_code", status_code=status.HTTP_200_OK)
async def generate_code(
        user_create_data: Annotated[UserSignup, Depends(get_login_form)],
        service: Annotated[UserService, Depends(get_user_service(database.get_async_session))],
) -> JSONResponse:
    code = await service.generate_registration_code(user_data=user_create_data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        media_type="application/json",
        content={
            "code": code,
            "max_age_sec": 600
        }
    )


@router.post("/activate", status_code=status.HTTP_201_CREATED)
async def complete_signup(
        tg_chat_id: Annotated[int, Query()],
        code: Annotated[str, Query()],
        service: Annotated[UserService, Depends(get_user_service(database.get_async_session))],
) -> JSONResponse:
    await service.activate_user(
        code=code,
        tg_chat_id=tg_chat_id,
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        media_type="application/json",
        content={
            "message": "Successfully signed up a new user"
        }
    )


@router.get("/check_tg", status_code=status.HTTP_200_OK)
async def check_if_chat_id_used(
        response: Response,
        tg_chat_id: Annotated[int, Query()],
        service: Annotated[UserService, Depends(get_user_service(database.get_async_session))],
) -> Response:
    tg_chat_id_in_db = await service.check_if_chat_id_used(tg_chat_id=tg_chat_id)
    if tg_chat_id_in_db:
        response.status_code = status.HTTP_409_CONFLICT
    else:
        response.status_code = status.HTTP_200_OK
    return response


@router.post("/logout")
async def logout_user():
    ...
    #todo реализовать удаление токена из куки и из кеша redis

