import base64
import json
import logging

from api_server.core import Redis
from api_server.schemas import (
    UserLogin,
    UserSignup,
    UserInsertToDB,
    UserFromDB
)
from api_server.repositories import UserRepo
from api_server.exceptions import (
    NoSuchUserInDBException,
    WrongPasswordException,
    UserAlreadyExistException,
    InvalidCodeException,
)
from api_server.utils import (
    HashingTool,
    JwtTool,
    create_activation_code,
)

logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, user_repository: UserRepo) -> None:
        self.redis = Redis()
        self.repo = user_repository

    async def login_user(self, user_data: UserLogin) -> str:
        match_user = await self.repo.select_user_by_username(user_data.username)
        if not match_user:
            logger.debug(
                "User %s not found in database.",
                user_data.username
            )
            raise NoSuchUserInDBException()
        else:
            is_password_valid = HashingTool.verify(
                provided_password=user_data.password,
                hashed_password=match_user.hashed_password
            )
            if not is_password_valid:
                logger.debug(
                    "User with id: %s entered wrong password.",
                    match_user.id
                )
                raise WrongPasswordException()
            else:
                redis = await self.redis.get_connection()
                payload = {
                    "sub": match_user.id,
                    "name": match_user.username,
                    "tg_chat_id": match_user.tg_chat_id,
                }
                jwt_token = JwtTool.create_token(payload=payload)
                await redis.setex(
                    name=f"{match_user.id}:session",
                    time=86400,  # 24 hours in seconds
                    value=jwt_token,
                )
                logger.info(
                    "User with id: %s logged in.",
                    match_user.id
                )
                return jwt_token

    async def generate_registration_code(self, user_data: UserSignup) -> str:
        match_user = await self.repo.select_user_by_username(user_data.username)
        if match_user:
            logger.debug(
                "User %s already exists in database.",
                user_data.username
            )
            raise UserAlreadyExistException()
        else:
            payload_json = user_data.model_dump_json()
            activation_code = create_activation_code(payload_json)
            redis = await self.redis.get_connection()
            await redis.setex(
                name=activation_code,
                time=600,
                value=payload_json,
            )
            logger.info(
                "Registration code for user: %s generated. Code: %s",
                user_data.username,
                activation_code
            )
            return activation_code

    async def activate_code(self, code: str, tg_chat_id: int) -> None:
        redis = await self.redis.get_connection()
        user_signup_data_json_str = await redis.get(code)
        if not user_signup_data_json_str:
            logger.info(
                "User entered invalid code. Code: %s",
                code
            )
            raise InvalidCodeException()
        else:
            user_data = json.loads(user_signup_data_json_str)
            user_create_schema = UserInsertToDB(
                tg_chat_id=tg_chat_id,
                username=user_data["username"],
                hashed_password=HashingTool.encrypt(user_data["password"])
            )
            await self.repo.insert_user(user_create_schema)
            await redis.delete(code)
            logger.info(
                "User %s successfully signed up.",
                user_create_schema.username
            )

    async def check_if_chat_id_used(self, tg_chat_id: int) -> bool:
        user_with_tg_chat_id = await self.repo.select_by_tg_chat_id(tg_chat_id)
        return bool(user_with_tg_chat_id)

    async def clear_session(self, user_id: int) -> None:
        redis = await self.redis.get_connection()
        session_key = f"{user_id}:session"
        await redis.delete(session_key)
        logging.info(
            "Session for user with id: %s eliminated.",
            user_id
        )

    async def get_id_from_username(self, username: str) -> int:
        user = await self.repo.select_user_by_username(username)
        if not user:
            raise NoSuchUserInDBException()
        return user.id

    async def get_user_from_db(self, user_id: int) -> UserFromDB:
        user = await self.repo.select_user(user_id=user_id)
        if not user:
            raise NoSuchUserInDBException()
        user_schema = UserFromDB.model_validate(user)
        return user_schema
