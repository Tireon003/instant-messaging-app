import logging
from collections.abc import AsyncIterator, Sequence
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
    UserFromDB,
)

logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self, chat_repository: ChatRepo) -> None:
        self.redis: Redis = Redis()
        self.repo = chat_repository

    @asynccontextmanager
    async def observe_chat(
        self, user_id: int, chat_id: int
    ) -> AsyncIterator[None]:
        redis_conn = None
        key_user_on_chat = f"{user_id}:{chat_id}"
        logger.debug(
            "User with id: %s observing chat with id:",
            user_id,
            chat_id,
        )
        try:
            redis_conn = await self.redis.get_connection()
            await redis_conn.set(name=key_user_on_chat, value=1)
            yield
        finally:
            if redis_conn:
                await redis_conn.delete(key_user_on_chat)
            logger.debug(
                "User with id: %s stopped observing chat with id:",
                user_id,
                chat_id,
            )

    async def send_message(
        self,
        chat_id: int,
        from_user: UserFromDB,
        to_user: UserFromDB,
        message: str,
    ) -> str:
        redis_conn = await self.redis.get_connection()
        recipient_key = f"{to_user.id}:{chat_id}"
        recipient_online = await redis_conn.get(recipient_key)
        message_create_schema = MessageCreateInDB(
            chat_id=chat_id,
            owner=from_user.id,
            content=message,
            is_read=bool(recipient_online),
        )
        message_in_db = await self.repo.insert_message(message_create_schema)
        message_schema = MessageFromDB.model_validate(message_in_db)
        if not recipient_online:
            logger.info("Sending notification to user with id: %s", to_user.id)
            send_notification_to_user.delay(
                tg_chat_id=to_user.tg_chat_id,
                message=message_schema.content,
                from_user=from_user.username,
            )
        logger.info(
            "User with id: %s sent message to user with id: %s",
            from_user.id,
            to_user.id,
        )
        return message_schema.model_dump_json()

    async def get_chat_history(
        self, chat_id: int, user_id: int
    ) -> list[MessageFromDB] | None:
        redis_conn = await self.redis.get_connection()
        session_key_in_redis = f"{user_id}:session"
        key_found = await redis_conn.get(session_key_in_redis)
        if not key_found:
            logger.info(
                "Session of user with id: %s not found in session cache.",
                user_id,
            )
            raise InvalidSessionKeyException()
        messages_orm_models = await self.repo.select_messages(chat_id)
        await self.repo.update_messages(
            list(
                filter(
                    lambda msg: not msg.is_read and msg.owner != user_id,
                    messages_orm_models,
                )
            )
        )
        messages_schemas = [
            MessageFromDB.model_validate(msg) for msg in messages_orm_models
        ]
        logger.debug("Chat history for chat with id: %s collected.", chat_id)
        return messages_schemas

    async def create_new_chat(
        self, user_id: int, with_user: int
    ) -> ChatFromDB:
        logger.info(
            "Creating new chat between users with id: %s and %s.",
            user_id,
            with_user,
        )
        founded_chat = await self.repo.select_chat(
            user_1=user_id,
            user_2=with_user,
        )
        if founded_chat:
            logger.info(
                "Chat between users with id: %s and %s not created.",
                user_id,
                with_user,
            )
            raise ChatAlreadyExistException()
        else:
            create_chat_schema = ChatCreate(  # todo задокументировать, кто такой user_1 и user_2
                user_1=user_id,
                user_2=with_user,
            )
            new_chat = await self.repo.insert_chat(create_chat_schema)
            created_chat_schema = ChatFromDB.model_validate(new_chat)
            logger.info(
                "Chat between users with id: %s and %s created.",
                user_id,
                with_user,
            )
            return created_chat_schema

    async def get_chat_list(self, user_id: int) -> list[ChatAndRecipient]:
        logger.info("Getting chat list for user with id: %s...", user_id)
        chats = await self.repo.select_chats(user_id)
        logger.info("Got chat list for user with id: %s.", user_id)
        return chats

    async def get_read_status(
        self, messages: Sequence[int]
    ) -> dict[int, bool]:
        messages_orm = await self.repo.select_messages_by_ids(messages)
        messages_read_status = {
            message.id: message.is_read for message in messages_orm
        }
        return messages_read_status
