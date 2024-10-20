import base64
import json

from api_server.core import Redis
from api_server.schemas import UserLogin, UserSignup, UserInsertToDB
from api_server.repositories import UserRepo
from api_server.exceptions import (
    NoSuchUserInDBException,
    WrongPasswordException,
    UserAlreadyExistException,
    InvalidCodeException,
)
from api_server.utils import HashingTool, JwtTool


class UserService:

    def __init__(self, user_repository: UserRepo) -> None:
        self.redis = Redis()
        self.repo = user_repository

    async def set_user_online(self, user_id):
        redis = await self.redis.get_connection()
        await redis.setex(
            name=f"{user_id}:online",
            time=5,
            value=True,
        )

    async def login_user(self, user_data: UserLogin) -> str:
        match_user = await self.repo.select_user_by_username(user_data.username)
        if not match_user:
            raise NoSuchUserInDBException()
        else:
            is_password_valid = HashingTool.verify(
                provided_password=user_data.password,
                hashed_password=match_user.hashed_password
            )
            if not is_password_valid:
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
                return jwt_token

    async def generate_registration_code(self, user_data: UserSignup) -> str:
        match_user = await self.repo.select_user_by_username(user_data.username)
        if match_user:
            raise UserAlreadyExistException()
        else:
            payload_json = user_data.model_dump_json()
            base64_code_bytes = base64.b64encode(payload_json.encode('utf-8'))
            base64_code_str = base64_code_bytes.decode('utf-8')
            redis = await self.redis.get_connection()
            await redis.setex(
                name=base64_code_str,
                time=600,
                value=payload_json,
            )
            return base64_code_str

    async def activate_user(self, code: str, tg_chat_id: int) -> None:
        redis = await self.redis.get_connection()
        user_signup_data_json_str = await redis.get(code)
        if not user_signup_data_json_str:
            raise InvalidCodeException()
        else:
            user_data = json.loads(user_signup_data_json_str)
            user_data_for_db = {
                "tg_chat_id": tg_chat_id,
                "username": user_data["username"],
                "hashed_password": HashingTool.encrypt(user_data["password"])
            }
            user_create_schema = UserInsertToDB.model_validate(user_data_for_db)
            await self.repo.insert_user(user_create_schema)
            await redis.delete(code)

    async def check_if_chat_id_used(self, tg_chat_id: int) -> bool:
        user_matched_tg_chat_id = await self.repo.select_by_tg_chat_id(tg_chat_id)
        if user_matched_tg_chat_id:
            return True
        return False

    async def clear_session(self, user_id: int) -> None:
        redis = await self.redis.get_connection()
        session_key = f"{user_id}:session"
        await redis.delete(session_key)  # todo check deletion of non-existing key

    async def get_recipient_tg_chat_id(self, user_id: int) -> int | None:
        user = await self.repo.select_user(user_id)
        if not user:
            raise NoSuchUserInDBException()
        else:
            tg_chat_id = user.tg_chat_id
            return tg_chat_id

    async def get_id_from_username(self, username: str) -> int | None:
        user = await self.repo.select_user_by_username(username)
        if user:
            return user.id
        else:
            return None

    async def get_username(self, user_id: int) -> str | None:
        user = await self.repo.select_user(user_id)
        if user:
            return user.username
