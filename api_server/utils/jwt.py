import jwt
import datetime as dt

from api_server.config import settings
from api_server.exceptions import InvalidTokenException


class JwtTool:

    ALG = "HS256"
    SECRET = settings.JWT_SECRET

    @classmethod
    def create_token(cls, payload: dict):
        return jwt.encode(
            payload=payload,
            key=cls.SECRET,
            algorithm=cls.ALG
        )

    @classmethod
    def read_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, cls.SECRET, algorithms=[cls.ALG])
            return payload
        except jwt.InvalidTokenError:
            raise InvalidTokenException()
