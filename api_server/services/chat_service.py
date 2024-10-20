from contextlib import asynccontextmanager

from api_server.core import Redis
from api_server.exceptions import (
    InvalidSessionKeyException,
    ChatAlreadyExistException,
)
from api_server.repositories import ChatRepo
from api_server.tasks.notification_tasks import send_notification_to_user
from api_server.schemas import (
    MessageCreateInDB,
    MessageFromDB,
    ChatFromDB,
    ChatCreate,
    ChatAndRecipient,
)


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
                           to_user_username: str,
                           tg_chat_id: int) -> str:
        message_dict = {
            "chat_id": chat_id,
            "owner": owner,
            "content": message,
        }
        message = MessageCreateInDB.model_validate(message_dict)
        message_in_db = await self.repo.insert_message(message)
        message_schema = MessageFromDB.model_validate(message_in_db)
        redis_conn = await self.redis.get_connection()
        recipient_key = f"{to_user}:{chat_id}"
        recipient_online = await redis_conn.get(recipient_key)
        if not recipient_online:
            send_notification_to_user.delay(
                tg_chat_id=tg_chat_id,
                message=message.content,
                from_user=to_user_username,
            )
        return message_schema.model_dump_json()

    async def get_chat_history(self,
                               chat_id: int,
                               user_id: int) -> list[MessageFromDB] | None:
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

    async def create_new_chat(self,
                              user_id: int,
                              with_user: int) -> ChatFromDB:
        founded_chat = await self.repo.select_chat(
            user_1=user_id,
            user_2=with_user,
        )
        if founded_chat:
            raise ChatAlreadyExistException()
        else:
            create_chat_schema = ChatCreate.model_validate(
                {
                    "user_1": user_id,
                    "user_2": with_user,
                }
            )
            new_chat = await self.repo.insert_chat(create_chat_schema)
            created_chat_schema = ChatFromDB.model_validate(new_chat)
            return created_chat_schema

    async def get_chat_list(self,
                            user_id: int) -> list[ChatAndRecipient] | None:
        chats = await self.repo.select_chats(user_id)
        return chats
