from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api_server.schemas import TokenPayload, UserCredentials
from api_server.utils import JwtTool

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_token_payload(
        access_token: Annotated[
            str,
            Depends(oauth2_scheme)
        ]
) -> TokenPayload:
    payload_dict = JwtTool.read_token(access_token)
    payload_schema = TokenPayload.model_validate(payload_dict)
    return payload_schema


def get_token_payload_for_ws(token: Annotated[str, Query()]) -> TokenPayload:
    payload_dict = JwtTool.read_token(token)
    payload_schema = TokenPayload.model_validate(payload_dict)
    return payload_schema


def get_login_form(
        credentials: Annotated[
            UserCredentials,
            Depends(OAuth2PasswordRequestForm)
        ]
) -> UserCredentials:
    data = UserCredentials(
        username=credentials.username,
        password=credentials.password
    )
    return data
