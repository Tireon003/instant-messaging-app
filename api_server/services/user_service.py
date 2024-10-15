from api_server.core import Redis
from api_server.schemas import UserLogin


class UserService:

    def __init__(self, user_repository) -> None:
        self.repo = user_repository

    @staticmethod
    def set_user_online(user_id):
        redis = Redis.create_redis_connection()
        redis.setex(
            name=f"{user_id}:online",
            time=5,
            value=True,
        )

    async def login_user(self, user_data: UserLogin):
        ...  # todo написать логику входа в аккаунт, в случае проблем вызываем исключения, на ep обрабатываем