from contextlib import asynccontextmanager

from api_server.core import Redis
from api_server.exceptions import InvalidSessionKeyException
from api_server.repositories import ChatRepo
from api_server.tasks.notification_tasks import send_notification_to_user
from api_server.schemas import  MessageCreateInDB, MessageFromDB


class ChatService:

    def __init__(self, chat_repository: ChatRepo) -> None:
        self.redis = Redis()
        self.repo = chat_repository

    @asynccontextmanager
    async def observe_chat(self, user_id: int, chat_id: int):
        redis_conn = None
        key_user_on_chat = f"{user_id}:{chat_id}"
        try:
            redis_conn = await self.redis.get_connection()
            await redis_conn.set(
                name=key_user_on_chat,
                value=1
            )
            yield
        finally:
            if redis_conn:
                await redis_conn.delete(key_user_on_chat)

    async def send_message(self,
                           chat_id: int,
                           message: str,
                           owner: int,
                           to_user: int,
                           tg_chat_id: int) -> None:
        message_dict = {
            "chat_id": chat_id,
            "owner": owner,
            "content": message,
        }
        message = MessageCreateInDB.model_validate(message_dict)
        await self.repo.insert_message(message)
        redis_conn = await self.redis.get_connection()
        recipient_key = f"{to_user}:{chat_id}"
        recipient_online = await redis_conn.get(recipient_key)
        if not recipient_online:
            send_notification_to_user.delay(
                tg_chat_id=tg_chat_id,
                message=message
            )

    async def get_chat_history(self,
                               chat_id: int,
                               user_id: int) -> list[MessageFromDB] | None:
        # todo проверяем активность сессии прежде чем сделать запрос в БД
        redis_conn = await self.redis.get_connection()
        session_key_in_radis = f"{user_id}:session"
        key_found = await redis_conn.get(session_key_in_radis)
        if not key_found:
            raise InvalidSessionKeyException()
        messages_orm_models = await self.repo.select_messages(chat_id)
        messages_schemas = [
            MessageFromDB.model_validate(msg) for msg in messages_orm_models
        ]
        return messages_schemas

